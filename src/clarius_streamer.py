import pyclariuscast
from PIL import Image
import queue

class ClariusSettings:
  def __init__(self, ip, port, path, width=512, height=512):
    self.ip = ip
    self.port = port
    self.path = path
    self.width = width
    self.height = height

class FrameData:
  def __init__(self, image, timestamp, imu):
    self.image = image
    self.timestamp = timestamp
    self.imu = imu


## Global Variables Section ======================

# Global queue to store frames
FRAME_QUEUE = queue.Queue(maxsize=10)
 
# Global Caster Object
CASTER = None

# Global settings for the Clarius probe
CLARIUS_SETTINGS = None

# Global Debugging Flag
PRINT_DEBUG_INFO = False



## CAST API Callback Functions ==================

# called when a new processed image is streamed
# @param image the scan-converted image data
# @param width width of the image in pixels
# @param height height of the image in pixels
# @param sz full size of image
# @param micronsPerPixel microns per pixel
# @param timestamp the image timestamp in nanoseconds
# @param angle acquisition angle for volumetric data
# @param imu inertial data tagged with the frame
def newProcessedImage(image, width, height, sz, micronsPerPixel, timestamp, angle, imu):
  global FRAME_QUEUE, PRINT_DEBUG_INFO

  imu_object = None
  if (len(imu) > 0):
    imu_object = imu[0]

  try:
    if PRINT_DEBUG_INFO:
      if imu_object is None:
        print("-- [Clarius Streamer] new Img: ts,", timestamp, "no imu data")
      else:
        print("-- [Clarius Streamer] new Img: ts:", timestamp, "qw:", imu_object.qw, "qx:", imu_object.qx, "qy:", imu_object.qy, "qz:", imu_object.qz)

    bpp = sz / (width * height)
    if bpp == 4:
      img = Image.frombytes("RGBA", (width, height), image)
    else:
      img = Image.frombytes("L", (width, height), image)

    if FRAME_QUEUE.full():
      FRAME_QUEUE.get()

    FRAME_QUEUE.put(FrameData(img, timestamp, imu))
  except Exception as e:
    print("Error in newProcessedImage callback:", str(e))

  return


## called when a new raw image is streamed
# @param image the raw pre scan-converted image data, uncompressed 8-bit or jpeg compressed
# @param lines number of lines in the data
# @param samples number of samples in the data
# @param bps bits per sample
# @param axial microns per sample
# @param lateral microns per line
# @param timestamp the image timestamp in nanoseconds
# @param jpg jpeg compression size if the data is in jpeg format
# @param rf flag for if the image received is radiofrequency data
# @param angle acquisition angle for volumetric data
def newRawImage(image, lines, samples, bps, axial, lateral, timestamp, jpg, rf, angle):
  # check the rf flag for radiofrequency data vs raw grayscale
  # raw grayscale data is non scan-converted and in polar co-ordinates
  # print(
  #    "raw image: {0}, {1}x{2} @ {3} bps, {4:.2f} um/s, {5:.2f} um/l, rf: {6}".format(
  #        timestamp, lines, samples, bps, axial, lateral, rf
  #    ), end = "\r"
  # )
  # if jpg == 0:
  #    img = Image.frombytes("L", (samples, lines), image, "raw")
  # else:
  #    # note! this probably won't work unless a proper decoder is written
  #    img = Image.frombytes("L", (samples, lines), image, "jpg")
  # img.save("raw_image.jpg")
  return


## called when a new spectrum image is streamed
# @param image the spectral image
# @param lines number of lines in the spectrum
# @param samples number of samples per line
# @param bps bits per sample
# @param period line repetition period of spectrum
# @param micronsPerSample microns per sample for an m spectrum
# @param velocityPerSample velocity per sample for a pw spectrum
# @param pw flag that is true for a pw spectrum, false for an m spectrum
def newSpectrumImage(image, lines, samples, bps, period, micronsPerSample, velocityPerSample, pw):
  return


## called when a new imu data is streamed
# @param imu inertial data tagged with the frame
def newImuData(imu):
  # global PRINT_DEBUG_INFO
  # try:
  #     if PRINT_DEBUG_INFO:
  #         print("--[Clarius Streamer] IMU Data:", imu)
  #         print("Timestamp:", imu.tm)
  #         print("Gyroscope:", imu.gx, imu.gy, imu.gz)
  #         print("Accelerometer:", imu.ax, imu.ay, imu.az)
  #         print("Magnetometer:", imu.mx, imu.my, imu.mz)
  #         print("Quaternion:", imu.qw, imu.qx, imu.qy, imu.qz)
  # except Exception as e:
  #     print("Error accessing IMU data:", str(e))
  #     # Prevent exception propagation through Qt
  #     pass
  # return
  pass


## called when freeze state changes
# @param frozen the freeze state
def freezeFn(frozen):
  if frozen:
    print("\nimaging frozen")
  else:
    print("imaging running")
  return


## called when a button is pressed
# @param button the button that was pressed
# @param clicks number of clicks performed
def buttonsFn(button, clicks):
  print("button pressed: {0}, clicks: {1}".format(button, clicks))
  return


## Streamer API Functions ==================

def configure(ip, port, path, width=512, height=512):
  global CASTER, CLARIUS_SETTINGS  # Ensure global variables are updated

  CASTER = pyclariuscast.Caster(
    newProcessedImage,
    newRawImage,
    newSpectrumImage,
    newImuData,
    freezeFn,
    buttonsFn
  )

  CLARIUS_SETTINGS = ClariusSettings(ip, port, path, width, height)

  CASTER.init(path, width, height)


def start():
  global CASTER
  CASTER.connect(CLARIUS_SETTINGS.ip, CLARIUS_SETTINGS.port, "research")
  print("-- [Clarius Streamer] Connected to probe at {0}:{1}".format(CLARIUS_SETTINGS.ip, CLARIUS_SETTINGS.port))


def stop():
  global CASTER
  CASTER.destroy()
  print("-- [Clarius Streamer] Caster destroyed")


def get_frame():
  global FRAME_QUEUE

  if not FRAME_QUEUE.empty():
    return FRAME_QUEUE.queue[-1]  # Access the most recent frame using the `queue` attribute
  else:
    return None
  

def set_print_debug_info(debug: bool):
  global PRINT_DEBUG_INFO
  PRINT_DEBUG_INFO = debug
  if PRINT_DEBUG_INFO:
    print("-- [Clarius Streamer] Debugging information enabled")
  else:
    print("-- [Clarius Streamer] Debugging information disabled")


if __name__ == "__main__":

  ip = "192.168.1.1"
  port = 5828

  # get home path
  path = 'research'

  # create a ClariusStreamer instance
  configure(ip, port, path, 512, 512)
  start()

   # input loop
  while True:
    pass
