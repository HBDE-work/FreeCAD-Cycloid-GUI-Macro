from math import atan, cos, pi, sin

import FreeCAD as App
import Part
import Sketcher
from PySide import QtWidgets

DEFAULT_ROLLER_COUNT = 35
DEFAULT_ROTOR_RADIUS = 68 # [mm]
DEFAULT_ROLLER_RADIUS = 3.3 # [mm]
DEFAULT_EXCENTRICITY = 1.5 # [mm]
DEFAULT_PARAMETRIC_RESOLUTION = 5000
DEFAULT_DEBUGGING: bool = False

def rescale_func(x, roller_count:int, factor:float = 0.7):
    # choose factor between 0 and 1
    return x + factor * sin(x * (roller_count - 1) * 2 * pi +  pi) / (2 * (roller_count - 1) *  pi)

class ParameterDialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rotor Parameters")

        layout = QtWidgets.QFormLayout()

        # Amount of rollers
        self.roller_count = QtWidgets.QSpinBox()
        self.roller_count.setRange(1, 1000)
        self.roller_count.setValue(DEFAULT_ROLLER_COUNT)
        self.roller_count.setToolTip("Number of rollers")
        layout.addRow("Amount of rollers:", self.roller_count)

        # Rotor radius
        self.rotor_radius = QtWidgets.QDoubleSpinBox()
        self.rotor_radius.setRange(0.001, 1000000.0)
        self.rotor_radius.setDecimals(3)
        self.rotor_radius.setValue(DEFAULT_ROTOR_RADIUS)
        self.rotor_radius.setSuffix(" mm")
        self.rotor_radius.setToolTip("Radius of the rotor")
        layout.addRow("Rotor radius:", self.rotor_radius)

        # Roller radius
        self.roller_radius = QtWidgets.QDoubleSpinBox()
        self.roller_radius.setRange(0.001, 1000000.0)
        self.roller_radius.setDecimals(3)
        self.roller_radius.setValue(DEFAULT_ROLLER_RADIUS)
        self.roller_radius.setSuffix(" mm")
        self.roller_radius.setToolTip("Radius of the rollers")
        layout.addRow("Roller radius:", self.roller_radius)

        # excentricity
        self.excentricity = QtWidgets.QDoubleSpinBox()
        self.excentricity.setRange(0.001, 1000000.0)
        self.excentricity.setDecimals(3)
        self.excentricity.setValue(DEFAULT_EXCENTRICITY)
        self.excentricity.setSuffix(" mm")
        self.excentricity.setToolTip(
            "excentricity (offset) from the input shaft "
            "to the center of the rotor"
        )
        layout.addRow("excentricity / offset:", self.excentricity)

        # Parametrization steps
        self.parametric_resolution = QtWidgets.QSpinBox()
        self.parametric_resolution.setRange(2, 1000000)
        self.parametric_resolution.setValue(DEFAULT_PARAMETRIC_RESOLUTION)
        self.parametric_resolution.setToolTip("Number of points used for parametrization")
        layout.addRow("Parametrization steps:", self.parametric_resolution)

        # Debugging
        self.debugging = QtWidgets.QCheckBox()
        self.debugging.setChecked(DEFAULT_DEBUGGING)
        self.debugging.setToolTip("Enable debugging / matplotlib visualization")
        layout.addRow("Debugging:", self.debugging)

        # OK / Cancel buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok |
            QtWidgets.QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)

        self.setLayout(layout)


class Epitrochoid:
    def __init__(self,
        rotor_radius,
        roller_radius,
        excentricity,
        roller_count
    ):
        self.rotor_radius = rotor_radius # radius of the Rotor
        self.roller_radius = roller_radius # radius of the Rollers
        self.roller_count = roller_count # number of Rollers
        self.excentricity = excentricity # excentricity (or offset) from the Input Shaft to the center of the Rotor

    def psi(self, theta):
        return atan(sin((self.roller_count - 1)*theta) / ((self.rotor_radius / (self.excentricity * self.roller_count)) - cos((self.roller_count - 1)*theta)))

    def x(self,theta):
        Psi = self.psi(theta)
        return self.rotor_radius * cos(theta) - self.roller_radius * cos(theta - Psi) - self.excentricity * cos(self.roller_count * theta)

    def y(self,theta):
        Psi = self.psi(theta)
        return - self.rotor_radius * sin(theta) + self.roller_radius * sin(theta - Psi) + self.excentricity * sin(self.roller_count * theta)

class EpitrochoidSketcher:
    def __init__(self,epitrochoid,steps=1000):
        self.steps = steps
        self.epitrochoid = epitrochoid
        self.doc = App.ActiveDocument
        self.sketch = self.doc.addObject("Sketcher::SketchObject", "Cycloid")

    def run(self):
        # generate coordinates
        thetaList = [rescale_func(j / self.steps, self.epitrochoid.roller_count, 0.8) for j in range(self.steps + 1)]
        xList = [self.epitrochoid.x(theta * 2 * pi) for theta in thetaList]
        yList = [self.epitrochoid.y(theta * 2 * pi) for theta in thetaList]
        # add lines to the sketch
        for j in range(self.steps):
            x1, x2 = xList[j:j+2]
            y1, y2 = yList[j:j+2]
            self.sketch.addGeometry(Part.LineSegment(App.Vector(x1, y1, 0),
                                        App.Vector(x2, y2, 0)), False)
        self.sketch.addConstraint(Sketcher.Constraint("Coincident", 0, 1, self.steps - 1, 2))
        self.doc.recompute()

def main():
    # Show the dialog
    dialog = ParameterDialog()

    if not dialog.exec():
        App.Console.PrintMessage("Operation cancelled.\n")
        return

    roller_count = dialog.roller_count.value()
    rotor_radius = dialog.rotor_radius.value()
    roller_radius = dialog.roller_radius.value()
    excentricity  = dialog.excentricity.value()
    parametric_resolution = dialog.parametric_resolution.value()

    epi = Epitrochoid(rotor_radius,roller_radius,excentricity,roller_count)
    es = EpitrochoidSketcher(epi,parametric_resolution)
    es.run()

    if dialog.debugging.isChecked():
        try:
            import matplotlib.pyplot as plt
            thetaList = [j / 1000 * 2 * pi for j in range(1000)]
            xList = [epi.x(theta) for theta in thetaList]
            yList = [epi.y(theta) for theta in thetaList]
            _fig, _ax = plt.subplots(figsize=(7,7))
            plt.plot(xList,yList)
            plt.show()
        except Exception:
            App.Console.PrintError("Install matplotlib and / or numpy for debugging mode to work.")

if __name__ == '__main__':
    main()
