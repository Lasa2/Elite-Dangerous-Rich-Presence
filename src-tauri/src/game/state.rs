use serde::{Deserialize, Serialize};
use ts_rs::TS;

use super::journal::JournalEvent;

/// Current activity status in the game
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS, Default)]
#[ts(export)]
pub enum ActivityStatus {
    #[default]
    Launcher,
    MainMenu,
    Docked,
    NormalSpace,
    Supercruise,
    Landed,
    InSrv,
    OnFootStation,
    OnFootPlanet,
}

/// Current game state tracked from journal events
#[derive(Debug, Clone, Serialize, Deserialize, TS, Default)]
#[ts(export)]
pub struct GameState {
    /// Commander name
    pub commander: Option<String>,
    /// Current star system
    pub star_system: Option<String>,
    /// Current body (planet/station/etc)
    pub body: Option<String>,
    /// Current station name (if docked)
    pub station: Option<String>,
    /// Current ship type (internal name like "sidewinder")
    pub ship: Option<String>,
    /// Current ship name (player-given name)
    pub ship_name: Option<String>,
    /// Current game mode (Solo, Open, Private)
    pub game_mode: Option<String>,
    /// Current activity status
    pub status: ActivityStatus,
    /// Whether in a taxi (Apex shuttle)
    pub in_taxi: bool,
    /// Whether in multicrew
    pub in_multicrew: bool,
    /// Current Power (Powerplay)
    pub power: Option<String>,
    /// Session start timestamp (Unix seconds)
    pub session_start: Option<u64>,
    /// Whether this is a legacy (Horizons 3.8) session
    pub is_legacy: bool,
}

impl GameState {
    pub fn new() -> Self {
        Self::default()
    }

    /// Reset state to launcher defaults
    pub fn reset(&mut self) {
        *self = Self {
            session_start: self.session_start,
            ..Default::default()
        };
    }

    /// Process a journal event and update state
    pub fn process_event(&mut self, event: &JournalEvent) {
        match event {
            JournalEvent::Fileheader {
                timestamp,
                gameversion,
                ..
            } => {
                self.reset();
                self.status = ActivityStatus::MainMenu;
                self.star_system = Some("Main Menu".to_string());
                // Check for legacy (Horizons 3.8.x)
                if let Some(version) = gameversion {
                    self.is_legacy = version.starts_with("3.8");
                }
                // Parse session start time
                if let Ok(dt) = chrono::DateTime::parse_from_rfc3339(timestamp) {
                    self.session_start = Some(dt.timestamp() as u64);
                }
            }

            JournalEvent::LoadGame {
                commander,
                ship,
                ship_name,
                game_mode,
                ..
            } => {
                self.commander = Some(commander.clone());
                if let Some(s) = ship {
                    self.ship = Some(s.to_lowercase());
                }
                self.ship_name = ship_name.clone();
                self.game_mode = game_mode.clone();
            }

            JournalEvent::Location {
                star_system,
                body,
                station_name,
                docked,
                taxi,
                multicrew,
                in_srv,
                on_foot,
                ..
            } => {
                self.star_system = Some(star_system.clone());
                self.body = body.clone();
                self.station = station_name.clone();
                self.in_taxi = *taxi;
                self.in_multicrew = *multicrew;

                if *on_foot {
                    if station_name.is_some() {
                        self.status = ActivityStatus::OnFootStation;
                    } else {
                        self.status = ActivityStatus::OnFootPlanet;
                    }
                } else if *in_srv {
                    self.status = ActivityStatus::InSrv;
                } else if *docked {
                    self.status = ActivityStatus::Docked;
                } else {
                    self.status = ActivityStatus::NormalSpace;
                }
            }

            JournalEvent::FSDJump { star_system, .. } => {
                self.star_system = Some(star_system.clone());
                self.body = None;
                self.station = None;
                self.status = ActivityStatus::Supercruise;
            }

            JournalEvent::CarrierJump {
                star_system,
                docked,
                ..
            } => {
                self.star_system = Some(star_system.clone());
                if *docked {
                    self.status = ActivityStatus::Docked;
                }
            }

            JournalEvent::SupercruiseEntry { star_system, .. } => {
                if let Some(system) = star_system {
                    self.star_system = Some(system.clone());
                }
                self.status = ActivityStatus::Supercruise;
                self.body = None;
            }

            JournalEvent::SupercruiseExit {
                star_system, body, ..
            } => {
                if let Some(system) = star_system {
                    self.star_system = Some(system.clone());
                }
                self.body = body.clone();
                self.status = ActivityStatus::NormalSpace;
            }

            JournalEvent::Docked {
                station_name,
                star_system,
                ..
            } => {
                self.station = Some(station_name.clone());
                if let Some(system) = star_system {
                    self.star_system = Some(system.clone());
                }
                self.status = ActivityStatus::Docked;
            }

            JournalEvent::Undocked { .. } => {
                self.station = None;
                self.status = ActivityStatus::NormalSpace;
            }

            JournalEvent::Loadout {
                ship,
                ship_name,
                ..
            } => {
                self.ship = Some(ship.to_lowercase());
                self.ship_name = ship_name.clone();
            }

            JournalEvent::Touchdown { on_station, .. } => {
                if *on_station {
                    // Landed at a station
                } else {
                    self.status = ActivityStatus::Landed;
                }
            }

            JournalEvent::Liftoff { .. } => {
                self.status = ActivityStatus::NormalSpace;
            }

            JournalEvent::LaunchSRV { .. } => {
                self.status = ActivityStatus::InSrv;
            }

            JournalEvent::DockSRV { .. } => {
                self.status = ActivityStatus::Landed;
            }

            JournalEvent::Disembark {
                on_station,
                on_planet,
                taxi,
                ..
            } => {
                self.in_taxi = *taxi;
                if *on_station {
                    self.status = ActivityStatus::OnFootStation;
                } else if *on_planet {
                    self.status = ActivityStatus::OnFootPlanet;
                }
            }

            JournalEvent::Embark {
                taxi,
                station_name,
                ..
            } => {
                self.in_taxi = *taxi;
                if station_name.is_some() {
                    self.status = ActivityStatus::Docked;
                } else {
                    self.status = ActivityStatus::Landed;
                }
            }

            JournalEvent::ApproachBody { body, .. } => {
                self.body = Some(body.clone());
            }

            JournalEvent::LeaveBody { .. } => {
                self.body = None;
            }

            JournalEvent::Music { music_track, .. } => {
                // Main menu music indicates we're at the main menu
                if music_track == "MainMenu" {
                    self.status = ActivityStatus::MainMenu;
                    self.star_system = Some("Main Menu".to_string());
                }
            }

            JournalEvent::Powerplay { power, .. } => {
                self.power = Some(power.clone());
            }

            JournalEvent::PowerplayJoin { power, .. } => {
                self.power = Some(power.clone());
            }

            JournalEvent::PowerplayDefect { to_power, .. } => {
                self.power = Some(to_power.clone());
            }

            JournalEvent::PowerplayLeave { .. } => {
                self.power = None;
            }

            JournalEvent::JoinACrew { captain, .. } => {
                self.in_multicrew = true;
                if let Some(captain) = captain {
                    log::debug!("Joined crew of {}", captain);
                }
            }

            JournalEvent::QuitACrew { .. } | JournalEvent::EndCrewSession { .. } => {
                self.in_multicrew = false;
            }

            JournalEvent::Shutdown { .. } => {
                self.status = ActivityStatus::Launcher;
                self.star_system = Some("Launcher".to_string());
            }

            _ => {}
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ts_rs::TS;

    #[test]
    fn test_initial_state() {
        let state = GameState::new();
        assert_eq!(state.status, ActivityStatus::Launcher);
        assert!(state.commander.is_none());
    }

    #[test]
    fn test_fileheader_resets_state() {
        let mut state = GameState::new();
        state.commander = Some("Test".to_string());
        state.star_system = Some("Sol".to_string());

        state.process_event(&JournalEvent::Fileheader {
            timestamp: "2024-01-15T10:00:00Z".to_string(),
            gameversion: Some("4.0.0.1".to_string()),
            build: None,
            language: None,
        });

        assert_eq!(state.status, ActivityStatus::MainMenu);
        assert!(state.commander.is_none());
        assert_eq!(state.star_system, Some("Main Menu".to_string()));
    }

    #[test]
    fn test_loadgame_sets_commander() {
        let mut state = GameState::new();

        state.process_event(&JournalEvent::LoadGame {
            timestamp: "2024-01-15T10:00:00Z".to_string(),
            commander: "CMDR Test".to_string(),
            ship: Some("Sidewinder".to_string()),
            ship_name: Some("My Ship".to_string()),
            game_mode: Some("Solo".to_string()),
            fid: None,
        });

        assert_eq!(state.commander, Some("CMDR Test".to_string()));
        assert_eq!(state.ship, Some("sidewinder".to_string()));
        assert_eq!(state.ship_name, Some("My Ship".to_string()));
    }

    #[test]
    fn export_bindings_gamestate() {
        GameState::export_all().unwrap();
    }

    #[test]
    fn export_bindings_activitystatus() {
        ActivityStatus::export_all().unwrap();
    }
}
