from typing import List, Union
from overrides import override
from odrive.enums import InputMode, ControlMode
import mumei
from .ODriveController import ODriveController


class VelocityMotor(mumei.Motor):
    """
    Initialization to start reading the motor
    """

    def __init__(self, odrive_controller: ODriveController):
        # Init CAN port and store database
        self._current_limit = None
        self._velocity_limit = None
        self._desired_value = 0
        self._odrive = odrive_controller

    @override
    def configure(self, *args, **kwargs) -> None:
        """Configure velocity motor.

        Parameters:
        velocity_limit (float)
        current_limit (float)
        """
        self._velocity_limit = kwargs['velocity_limit']
        self._current_limit = kwargs['current_limit']

        self._odrive.configure(
            velocity_limit=self._velocity_limit,
            current_limit=self._current_limit,
            input_mode=InputMode.PASSTHROUGH,
            control_mode=ControlMode.VELOCITY_CONTROL)

    @override
    def initialize(self, *args, **kwargs) -> None:
        pass

    @override
    def set_up(self, *args, **kwargs) -> None:
        self._odrive.set_up()

    @override
    def move(self, val: Union[float, List[float]], *args, **kwargs) -> bool:
        print(f"Motor {self._odrive.can_id}: Setting torque to {val}")
        self._desired_value = val
        self._odrive.send_cmd("Set_Input_Torque", {'Input_Torque': val})
        return True

    @override
    def stop(self, *args, **kwargs) -> bool:
        print(f"Motor {self._odrive.can_id}: Stopped")
        return self.move_motor(0)

    @override
    def terminate(self, *args, **kwargs) -> None:
        """
        Terminate the component.
        """
        pass

    @override
    def reach_goal(self) -> bool:
        """
        Returns true if the motor reaches the desired value
        """
        # threshold = 0.6
        # msg = self.bus.recv()
        # arbID = ((self.axis << 5) | self.db.get_message_by_name(
        #     'Get_Encoder_Estimates').frame_id)
        # if msg.arbitration_id == arbID:
        #     pos = self.db.decode_message('Get_Encoder_Estimates', msg.data)[
        #         'Pos_Estimate']
        #     vel = self.db.decode_message('Get_Encoder_Estimates', msg.data)[
        #         'Vel_Estimate']
        #     tor = pos * vel  # TODO: fix this, temp only
        #     if self.axis > -1:
        #         if print_value:
        #             print("Axis")
        #             print(self.axis)
        #             print("Desired Torque")
        #             print(self.desired_value)
        #             print("Current Torque")
        #             print("IDK calculate from velocity and pos ?!?")
        #             print("Error")
        #             print(abs(pos - self.desired_pos))
        #             print("")
        #     return abs(tor - self.desired_value) <= threshold  # TODO:change this to torque
        return False
