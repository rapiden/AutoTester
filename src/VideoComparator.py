import cv2 as cv
import numpy as np
from Exceptions import ImageComparatorError
from ImageComparator import ImageComparator
import os


class VideoComparator:
    def __init__(self, reference_video_path: str, output_result__path: str, top_left, bottom_right, tolerance, threshold=0.99):
        if os.path.isfile(reference_video_path) is False:
            raise ImageComparatorError(f'Reference video file does not exist: {reference_video_path}')
        self._video = cv.VideoCapture(reference_video_path)
        self._output_result__path = output_result__path

        self._top_left = top_left
        self._bottom_right = bottom_right

        self._tolerance = tolerance

        self._threshold = threshold
        self._threshold_epsilon = 1e-5
        self._transparent_color = (0, 0, 255)

    def flash_count(self, golden_image, golden_image2, times):
        flashing = False
        count = 0
        fourcc = cv.VideoWriter_fourcc(*'XVID')
        width = int(self._video.get(3))
        height = int(self._video.get(4))
        fps = self._video.get(cv.CAP_PROP_FPS)
        out = cv.VideoWriter(self._output_result__path, fourcc, fps, (width, height))

        golden_img = ImageComparator(None, golden_image, None, True, self._threshold)
        golden_img2 = ImageComparator(None, golden_image2, None, True, self._threshold)
        while self._video.isOpened():
            ret, frame = self._video.read()
            if ret:
                golden_img._reference_image_path = frame
                is_match = golden_img.compare_pattern(self._top_left, self._bottom_right, self._tolerance)
                if is_match:
                    self._draw_rectangle(frame, (255, 0, 0), 2)
                    if not flashing:
                        flashing = True
                        count += 1
                else:
                    golden_img2._reference_image_path = frame
                    is_match = golden_img2.compare_pattern(self._top_left, self._bottom_right, self._tolerance)
                    if is_match:
                        self._draw_rectangle(frame, (150, 0, 0), 0)
                        if flashing:
                            flashing = False
                out.write(frame)
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
        self._video.release()
        out.release()
        cv.destroyAllWindows()
        if count == times:
            return 'PASSED', count
        return 'FAILED', count

    def _draw_rectangle(self, frame, color, size):
        cv.rectangle(frame, (self._top_left[0] - self._tolerance, self._top_left[1] - self._tolerance),
                     (self._bottom_right[0] + self._tolerance, self._bottom_right[1] + self._tolerance), color, size)
