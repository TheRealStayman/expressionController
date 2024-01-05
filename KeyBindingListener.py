from pynput.keyboard import Key, KeyCode, Listener


class KeyboardListener:
    def __init__(self):
        # The currently pressed keys (initially empty)
        self.pressed_vks = set()
        self.tracked_vks = set()
        self.keys = ""
        self.deactivate_listener = False
    
    
    def get_vk(self, key):
        """
        Get the virtual key code from a key.
        These are used so case/shift modifications are ignored.
        """
        return key.vk if hasattr(key, 'vk') else key.value.vk
    
    
    def is_combination_pressed(self, combination):
        """ Check if a combination is satisfied using the keys pressed in self.pressed_vks """
        return all([self.get_vk(key) in self.pressed_vks for key in combination])
    
    
    def on_press(self, key):
        """ When a key is pressed """
        vk = self.get_vk(key)  # Get the key's vk
        self.pressed_vks.add(vk)  # Add it to the set of currently pressed keys
        if len(self.tracked_vks) > 1:
            if list(self.tracked_vks)[0] in [162, 163, 164, 165, 160, 161, 18, 17, 16]:
                self.tracked_vks.add(vk)
            else:
                if len(self.tracked_vks) > 2:
                    if list(self.tracked_vks)[1] in [162, 163, 164, 165, 160, 161, 18, 17, 16]:
                        self.tracked_vks.add(vk)
                    else:
                        if len(self.tracked_vks) > 3:
                            if list(self.tracked_vks)[2] in [162, 163, 164, 165, 160, 161, 18, 17, 16]:
                                self.tracked_vks.add(vk)
        else:
            self.tracked_vks.add(vk)
    
    
    def on_release(self, key):
        """ When a key is released """
        vk = self.get_vk(key)  # Get the key's vk
        self.pressed_vks.remove(vk)  # Remove it from the set of currently pressed keys
    
        if len(self.pressed_vks) == 0:
            print(str(self.tracked_vks))
            self.keys = str(self.tracked_vks)
            self.tracked_vks.clear()
            self.listener.stop()
    
    
    def activate_listener(self):
        with Listener(on_press=self.on_press, on_release=self.on_release) as self.listener:
            self.listener.join()
