import sys
from json import JSONEncoder


class StreamingJsonListPrinter():
  """ A streaming JSON list printer.

  This is used to output a JSON list from a Python generator/iterator without the need to
  convert it to a list before encoding it to JSON. This saves on memory when outputing very
  large lists.

  Cribbed from: https://nbsoftsolutions.com/blog/processing-arbitrary-amount-of-data-in-python.html
  """
  class SerializableGenerator(list):
    """ A wrapper class that spoofs the list interface for a generator so that the JSON
    encoder will iterate over it. """
    def __init__(self, generator):
      self.generator = generator

    def __iter__(self):
      return self.generator

    def __len__(self):
      return 1

  @staticmethod
  def dump(iterator, f=sys.stdout):
    """ Converts a Python generator (iterator) to a JSON list and
    outputs to a file handle (f) (defaults to sys.stdout)"""
    encoder = JSONEncoder(indent=2)
    for chunk in encoder.iterencode(StreamingJsonListPrinter.SerializableGenerator(iterator)):
      f.write(chunk)
      f.flush()
