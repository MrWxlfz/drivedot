#pragma once
#include <stdint.h>

namespace drivedot {
enum class ButtonEvent { None, ShortPress, LongPress };

// Pass true for an electrically low (pressed) input. Actions occur once, after
// debouncing; a long hold consumes its release rather than starting a session.
class Button {
 public:
  ButtonEvent update(bool rawPressed, uint32_t now) {
    if (rawPressed != raw_) { raw_ = rawPressed; changedAt_ = now; }
    if (now - changedAt_ >= 35 && raw_ != pressed_) {
      pressed_ = raw_;
      if (pressed_) { pressedAt_ = now; consumed_ = false; }
      else if (!consumed_) {
        consumed_ = true;
        // A slow loop may not have observed the hold threshold before release.
        return now - pressedAt_ >= 1500 ? ButtonEvent::LongPress
                                        : ButtonEvent::ShortPress;
      }
    }
    if (pressed_ && raw_ && !consumed_ && now - pressedAt_ >= 1500) {
      consumed_ = true;
      return ButtonEvent::LongPress;
    }
    return ButtonEvent::None;
  }
  bool pressed() const { return pressed_; }
  void suppressRelease() { consumed_ = true; }
 private:
  bool raw_ = false, pressed_ = false, consumed_ = false;
  uint32_t changedAt_ = 0, pressedAt_ = 0;
};
}
