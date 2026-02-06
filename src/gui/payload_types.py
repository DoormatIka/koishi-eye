
from typing import Literal
from gui.models.image import ModelImage


SelectedImageResult = tuple[Literal["add", "delete"], ModelImage]
DirectoryResult = str
