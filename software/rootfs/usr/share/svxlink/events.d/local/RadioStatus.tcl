if {$::logic_name ne "ReflectorLogic"} { return }
namespace eval ReflectorLogic {
  variable ui_tg 0
  variable ui_talkers [dict create]
  proc ui_publish {} {
    variable ui_tg
    variable ui_talkers
    set receiving [expr {$ui_tg != 0 && [dict exists $ui_talkers $ui_tg]}]
    if {[catch {
      set f [open /dev/shm/sqlink-radio-state.tmp w]
      set talker ""
      if {$receiving} {set talker [dict get $ui_talkers $ui_tg]}
      regsub -all {[\r\n]} $talker " " talker
      puts $f "[pid] $ui_tg $receiving $talker"
      close $f
      file rename -force /dev/shm/sqlink-radio-state.tmp /dev/shm/sqlink-radio-state
    } err]} { puts "SQLink radio state: $err" }
  }
  rename tg_selected ui_original_tg_selected
  proc tg_selected {new_tg old_tg} {
    variable ui_tg
    set ui_tg $new_tg
    ui_publish
    ui_original_tg_selected $new_tg $old_tg
  }
  rename talker_start ui_original_talker_start
  proc talker_start {tg callsign} {
    variable ui_talkers
    dict set ui_talkers $tg $callsign
    ui_publish
    ui_original_talker_start $tg $callsign
  }
  rename talker_stop ui_original_talker_stop
  proc talker_stop {tg callsign} {
    variable ui_talkers
    if {[dict exists $ui_talkers $tg]} {dict unset ui_talkers $tg}
    ui_publish
    ui_original_talker_stop $tg $callsign
  }
  if {$::logic_name eq "ReflectorLogic"} {ui_publish}
}
