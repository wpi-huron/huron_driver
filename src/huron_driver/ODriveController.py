import can
import cantools
import time
import odrive


class ODriveController:
    def __init__(self, can_id: str, axis_id: int) -> None:
        # Init CAN port and store database
        self.axis = axis_id
        self.can_id = can_id
        self.db = cantools.database.load_file("odrive-cansimple.dbc")
        self._states = {"idle": 0x01, "calib": 0x03, "closeloop": 0x08}
        self.bus = can.Bus(can_id, bustype="socketcan")

    def send_cmd(self, name_of_command, cmd_input) -> None:
        msg = self.db.get_message_by_name(name_of_command)
        data = msg.encode(cmd_input)
        msg = can.Message(arbitration_id=self.axis << 5 | msg.frame_id,
                          is_extended_id=False, data=data)
        self.bus.send(msg)

    def change_state(self, s):
        try:
            self._states[s]
        except KeyError:
            print(f"Motor {self.can_id}: Unknown state")
        self.send_cmd('Set_Axis_State',
                      {'Axis_Requested_State': self._states[s]})

    def get_cmd(self, name_of_command, cmd_input):
        msg = self.bus.recv()
        arbID = ((self.axis << 5) |
                 self.db.get_message_by_name(name_of_command).frame_id)

        while True:
            msg = self.bus.recv()
            if msg.arbitration_id == arbID:
                break
        return self.db.decode_message(name_of_command, msg.data)[cmd_input]

    def configure(
            self,
            velocity_limit: float,
            current_limit: float,
            input_mode: odrive.enums.InputMode,
            control_mode: odrive.enums.ControlMode) -> bool:
        """
        Configure the velocity and current limits for the motor.
        """
        self.send_cmd('Set_Controller_Mode', {
            'Input_Mode': input_mode,
            'Control_Mode': control_mode})
        print("Controller mode set")
        time.sleep(1)
        self.send_cmd(
            'Set_Limits', {'Velocity_Limit': velocity_limit,
                           'Current_Limit': current_limit})
        print("Limits set")

    def set_up(self) -> None:
        """
        Put motor into closed-loop mode.
        """
        print("Entering closed loop")
        self.change_state("closeloop")

    def calibrate(self) -> None:
        print(f"Motor {self.can_id}: Calibrating...")
        self.change_state("calib")
        # time.sleep(25)  # Standard time for motor calibration
        print(f"Motor {self.can_id}: Done calibrating.")

    def terminate(self) -> None:
        self.change_state("idle")
        print(f"Motor {self.can_id}: Terminated.")
