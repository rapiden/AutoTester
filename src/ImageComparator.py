import os
import cv2 as cv
import numpy as np
from Exceptions import ImageComparatorError
from PKLGenerator import PKLGenerator


class ImageComparator:
    def __init__(self, reference_image_path: str, golden_image_path: str, output_result_image_path: str, is_absence_match: bool, log_callback=None, threshold=0.98):
        self._is_numpy_img = False
        if reference_image_path is None:
            self._is_numpy_img = True
        else:
            if os.path.isfile(reference_image_path) is False:
                raise ImageComparatorError(f'Reference image file does not exist: {reference_image_path}')

        if os.path.isfile(golden_image_path) is False:
            raise ImageComparatorError(f'Golden image file does not exist: {golden_image_path}')

        self._reference_image_path = reference_image_path

        self._golden_image_path = golden_image_path
        self._output_result_image_path = output_result_image_path

        self._is_absence_match = is_absence_match

        self._threshold = threshold
        self._threshold_epsilon = 1e-5

        self._transparent_color = (0, 0, 255)

        golden_image_name, golden_image_ext = os.path.splitext(self._golden_image_path)
        if golden_image_ext == '.pkl':
            self._is_pkl = True

        else:
            self._is_pkl = False

        if log_callback is None:
            self._log_callback = print
        else:
            self._log_callback = log_callback

        if self._is_numpy_img:
            # Disable logging for numpy image (video)
            self._log_callback = self._video_log

        self._log_callback(f'\t\tReference image: {self._reference_image_path}.')
        self._log_callback(f'\t\tGolden image: {self._golden_image_path}.')
        self._log_callback(f'\t\tOutput image: {self._output_result_image_path}.')

    def compare_pattern(self, reference_top_left: tuple, reference_bottom_right: tuple, tolerance: int) -> bool:
        if (len(reference_top_left) != 2) or (len(reference_bottom_right) != 2):
            raise ImageComparatorError('Top left and bottom right should have two non-negative values.')

        if self._is_numpy_img:
            reference_image = self._reference_image_path
        else:
            reference_image = self._open_image_file(self._reference_image_path)
        reference_top_left = (reference_top_left[0] - tolerance, reference_top_left[1] - tolerance)
        reference_bottom_right = (reference_bottom_right[0] + tolerance, reference_bottom_right[1] + tolerance)
        self._check_crop_bounds(reference_image, self._reference_image_path, reference_top_left, reference_bottom_right)
        reference_image_cropped = reference_image[reference_top_left[1]:reference_bottom_right[1], reference_top_left[0]:reference_bottom_right[0]].copy()

        self._log_callback(f'\t\t\tSearch box top left: X = {reference_top_left[0]} px; Y = {reference_top_left[1]} px.')
        self._log_callback(f'\t\t\tSearch box bottom right: X = {reference_bottom_right[0]} px; Y = {reference_bottom_right[1]} px.')
        self._log_callback(f'\t\t\tTolerance: {tolerance} px.')

        golden_image = self._open_golden_image_file()
        result_image = reference_image.copy()

        is_match, max_loc = self._compare_images(reference_image_cropped, golden_image)
        if not self._is_numpy_img:
            self._draw_rectangles(result_image, golden_image, is_match, max_loc, reference_top_left, reference_bottom_right)
        return is_match

    def compare_sub_image(self, reference_top_left: tuple, reference_bottom_right: tuple, golden_image_top_left: tuple, golden_image_bottom_right: tuple, tolerance: int) -> bool:
        if (len(reference_top_left) != 2) or (len(reference_bottom_right) != 2) or (len(golden_image_top_left) != 2) or (len(golden_image_bottom_right) != 2):
            raise ImageComparatorError('Top lefts and bottom rights should have two non-negative values.')

        reference_image = cv.imread(self._reference_image_path)
        reference_top_left = (reference_top_left[0] - tolerance, reference_top_left[1] - tolerance)
        reference_bottom_right = (reference_bottom_right[0] + tolerance, reference_bottom_right[1] + tolerance)
        self._check_crop_bounds(reference_image, self._reference_image_path, reference_top_left, reference_bottom_right)
        reference_image_cropped = reference_image[reference_top_left[1]:reference_bottom_right[1], reference_top_left[0]:reference_bottom_right[0]].copy()

        golden_image = self._open_golden_image_file()
        golden_image_top_left = (golden_image_top_left[0] - tolerance, golden_image_top_left[1] - tolerance)
        golden_image_bottom_right = (golden_image_bottom_right[0] + tolerance, golden_image_bottom_right[1] + tolerance)
        self._check_crop_bounds(golden_image, self._golden_image_path, golden_image_top_left, golden_image_bottom_right)
        golden_image_cropped = golden_image[golden_image_top_left[1]:golden_image_bottom_right[1], golden_image_top_left[0]:golden_image_bottom_right[0]].copy()

        result_image = reference_image.copy()

        is_match, max_loc = self._compare_images(reference_image_cropped, golden_image_cropped)
        self._draw_rectangles(result_image, golden_image_cropped, is_match, max_loc, reference_top_left, reference_bottom_right)

        self._log_callback(f'\t\t\tSearch box top left: X = {reference_top_left[0]} px; Y = {reference_top_left[1]} px.')
        self._log_callback(f'\t\t\tSearch box bottom right: X = {reference_bottom_right[0]} px; Y = {reference_bottom_right[1]} px.')
        self._log_callback(f'\t\t\tGrab box top left: X = {golden_image_top_left[0]} px; Y = {golden_image_top_left[1]} px.')
        self._log_callback(f'\t\t\tGrab box bottom right: X = {golden_image_bottom_right[0]} px; Y = {golden_image_bottom_right[1]} px.')

        return is_match

    def compare_pattern_rdp(self, horizontal_indicator: str, horizontal_degrees: float, vertical_indicator: str, vertical_degrees: float, tolerance: int) -> bool:
        if self._is_numpy_img:
            reference_image = self._reference_image_path
        else:
            reference_image = cv.imread(self._reference_image_path)
        template = self._open_golden_image_file()

        reference_height, reference_width, reference_channels = reference_image.shape
        golden_height, golden_width, golden_channels = template.shape

        pixels_per_degree = 39.0

        drp = [reference_width/2, (reference_height/2)]  # display reference point
        top_left = [0, 0]

        LR = 0
        UD = 0

        if horizontal_indicator.upper() == 'LEFT':
            LR = -1
        elif horizontal_indicator.upper() == 'RIGHT':
            LR = 0

        if horizontal_indicator.upper() == 'ABOVE':
            UD = -1
        elif horizontal_indicator.upper() == 'BELOW':
            UD = 0

        if (reference_width % 2) == 0:
            drp[0] += float(LR)

        if (reference_height % 2) == 0:
            drp[1] += float(UD)

        if horizontal_indicator.upper() == 'LEFT':
            top_left[0] = round(drp[0] - (pixels_per_degree * horizontal_degrees))
        elif horizontal_indicator.upper() == 'RIGHT':
            top_left[0] = round(drp[0] + (pixels_per_degree * horizontal_degrees))
        else:
            raise ImageComparatorError(f'Invalid option: {horizontal_indicator}.')

        if vertical_indicator.upper() == 'BELOW':
            top_left[1] = round(drp[1] + (pixels_per_degree * vertical_degrees))

        elif vertical_indicator.upper() == 'ABOVE':
            top_left[1] = round(drp[1] - (pixels_per_degree * vertical_degrees))
        else:
            raise ImageComparatorError(f'Invalid option: {vertical_indicator}.')

        # Fix top_left position according to golden image RP
        top_left = (int(top_left[0] - self.RP_Offset[0]),  int(top_left[1] - self.RP_Offset[1]))

        # Determinate box size according to the golden image size
        bottom_right = (int(top_left[0] + golden_width), int(top_left[1] + golden_height))

        self._log_callback(f"\t\t\tImage display reference point: {drp}")
        self._log_callback(f'\t\t\tHorizontal position: {horizontal_degrees} degrees to direction {horizontal_indicator}.')
        self._log_callback(f'\t\t\tVertical position: {vertical_degrees} degrees to direction {vertical_indicator}.')

        is_match = self.compare_pattern(top_left, bottom_right, tolerance)
        return is_match

    def _compare_images(self, reference_image, golden_image):
        self._check_golden_image_fits(reference_image, golden_image)

        mask = cv.inRange(golden_image, self._transparent_color, self._transparent_color)
        mask = cv.bitwise_not(mask)
        mask = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)

        # Apply template Matching.
        res = cv.matchTemplate(reference_image, golden_image, cv.TM_CCORR_NORMED, mask=mask)

        # Eliminate infinities and NaNs.
        res[np.logical_or(np.isinf(res), np.isnan(res))] = 0.0

        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        self._log_callback(f'\t\t\tMatch percentage: {max_val}%.')
        if (max_val >= self._threshold) and (max_val >= 0.0 - self._threshold_epsilon) and (max_val <= 1.0 + self._threshold_epsilon):
            is_match = True
        else:
            is_match = False

        if (self._is_absence_match is False and is_match is True) or (self._is_absence_match is True and is_match is False):
            is_match = True
        else:
            is_match = False

        return is_match, max_loc

    def _draw_rectangles(self, result_image, golden_image, is_match, max_loc, reference_top_left, reference_bottom_right):
        h, w = golden_image.shape[:-1]

        golden_image_top_left = (max_loc[0] + reference_top_left[0] - 1, max_loc[1] + reference_top_left[1] - 1)
        golden_image_bottom_right = (golden_image_top_left[0] + w + 1, golden_image_top_left[1] + h + 1)

        if is_match is True:
            cv.rectangle(result_image, golden_image_top_left, golden_image_bottom_right, (244, 244, 0), 1)
            selected_area_color = (244, 0, 0)
        else:
            if self._is_absence_match is True:
                selected_area_color = (244, 0, 0)

            else:
                selected_area_color = (0, 0, 244)

        cv.rectangle(result_image, (reference_top_left[0] - 1, reference_top_left[1] - 1), (reference_bottom_right[0] + 1, reference_bottom_right[1] + 1), selected_area_color, 1)
        # self._draw_rp(result_image, reference_top_left, max_loc, tolerance)
        cv.imwrite(self._output_result_image_path, result_image)

    def _check_crop_bounds(self, image_file, image_path, top_left, bottom_right):
        if top_left[1] >= bottom_right[1]:
            raise ImageComparatorError(f'Invalid bounds for {image_path}: top left Y coordinate ({str(top_left[1])}) should be less than bottom right Y coordinate ({str(bottom_right[1])}).')

        if top_left[0] >= bottom_right[0]:
            raise ImageComparatorError(f'Invalid bounds for {image_path}: top left X coordinate ({str(top_left[0])}) should be less than bottom right X coordinate ({str(bottom_right[0])}).')

        h, w = image_file.shape[:-1]
        if (top_left[0] < 0 or top_left[0] > w) or (bottom_right[0] < 0 or bottom_right[0] > w) \
                or (top_left[1] < 0 or top_left[1] > h) or (bottom_right[1] < 0 or bottom_right[1] > h):
            raise ImageComparatorError(f'Invalid bounds for {image_path}: crop position {top_left},{bottom_right} is outside image boundaries.')

        delta_x = bottom_right[0] - top_left[0]
        delta_y = bottom_right[1] - top_left[1]

        if delta_x > w:
            raise ImageComparatorError(f'Invalid bounds for {image_path}: cropped width {str(delta_x)} is greater than original width ({str(w)}).')

        if delta_y > h:
            raise ImageComparatorError(f'Invalid bounds for {image_path}: cropped height {str(delta_y)} is greater than original height ({str(h)}).')

    def _check_golden_image_fits(self, reference_image, golden_image):
        reference_h, reference_w = reference_image.shape[:-1]
        golden_h, golden_w = golden_image.shape[:-1]

        if golden_h > reference_h:
            raise ImageComparatorError(
                f'Invalid golden image size {self._golden_image_path}: golden image height ({str(golden_h)}) is greater than reference image height ({str(reference_h)}).')

        if golden_w > reference_w:
            raise ImageComparatorError(
                f'Invalid golden image size {self._golden_image_path}: golden image height ({str(golden_w)}) is greater than reference image height ({str(reference_w)}).')

    def _open_golden_image_file(self):
        if self._is_pkl is True:
            img_result, dic_pattern = PKLGenerator.pkl_to_image(self._golden_image_path)
            self.RP_Offset = dic_pattern['RP_Offset']

            open_cv_img = np.array(img_result)

            try:
                r_channel, g_channel, b_channel, a_channel = cv.split(open_cv_img)

            except:
                raise ImageComparatorError(f'Image in .pkl file does not have 4 channels: {self._golden_image_path}')

            a_channel = cv.bitwise_not(a_channel)
            open_cv_img = cv.merge((b_channel, g_channel, a_channel))

            return open_cv_img

        else:
            return self._open_image_file(self._golden_image_path)

    def _open_image_file(self, image_path):
        image = cv.imread(image_path)
        if image.size == 0:
            raise ImageComparatorError(f'Invalid image file: {image_path}')

        return image

    def _video_log(self, text):
        pass

    def _draw_rp(self, result_image, reference_top_left, max_loc, tolerance):
        # This is for de-bugging
        if not hasattr(self, 'RP_Offset'):
            return None

        cross_size = 3
        x = (int(round(self.RP_Offset[0]))) + max_loc[0]
        y = (int(round(self.RP_Offset[1]))) + max_loc[1]
        cv.line(result_image, (reference_top_left[0] + x - cross_size, reference_top_left[1] + y),
                (reference_top_left[0] + x + cross_size, reference_top_left[1] + y), (39, 127, 255), 1)
        cv.line(result_image, (reference_top_left[0] + x, reference_top_left[1] + y - cross_size),
                (reference_top_left[0] + x, reference_top_left[1] + y + cross_size), (39, 127, 255), 1)
        print(reference_top_left)
        rp_x = (int(round(self.RP_Offset[0])))
        rp_y = (int(round(self.RP_Offset[1])))
        bottom = (reference_top_left[0] + tolerance + rp_x, reference_top_left[1] + tolerance + rp_y)
        print(bottom)
        cv.rectangle(result_image, (640, 512), bottom, (255, 255, 255), 1)

