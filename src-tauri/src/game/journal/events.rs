use serde::{Deserialize, Serialize};
use ts_rs::TS;

/// Represents a parsed journal event.
/// Uses lenient parsing - unknown events are captured as `Unknown` with raw JSON.
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[serde(tag = "event")]
#[ts(export)]
pub enum JournalEvent {
    // ===== Startup & Shutdown =====
    Fileheader {
        timestamp: String,
        #[serde(default)]
        gameversion: Option<String>,
        #[serde(default)]
        build: Option<String>,
        #[serde(default)]
        language: Option<String>,
    },

    LoadGame {
        timestamp: String,
        #[serde(rename = "Commander")]
        commander: String,
        #[serde(rename = "Ship")]
        #[serde(default)]
        ship: Option<String>,
        #[serde(rename = "ShipName")]
        #[serde(default)]
        ship_name: Option<String>,
        #[serde(rename = "GameMode")]
        #[serde(default)]
        game_mode: Option<String>,
        #[serde(rename = "FID")]
        #[serde(default)]
        fid: Option<String>,
    },

    Shutdown {
        timestamp: String,
    },

    // ===== Location Events =====
    Location {
        timestamp: String,
        #[serde(rename = "StarSystem")]
        star_system: String,
        #[serde(rename = "Body")]
        #[serde(default)]
        body: Option<String>,
        #[serde(rename = "BodyType")]
        #[serde(default)]
        body_type: Option<String>,
        #[serde(rename = "Docked")]
        #[serde(default)]
        docked: bool,
        #[serde(rename = "StationName")]
        #[serde(default)]
        station_name: Option<String>,
        #[serde(rename = "Taxi")]
        #[serde(default)]
        taxi: bool,
        #[serde(rename = "Multicrew")]
        #[serde(default)]
        multicrew: bool,
        #[serde(rename = "InSRV")]
        #[serde(default)]
        in_srv: bool,
        #[serde(rename = "OnFoot")]
        #[serde(default)]
        on_foot: bool,
    },

    FSDJump {
        timestamp: String,
        #[serde(rename = "StarSystem")]
        star_system: String,
        #[serde(rename = "SystemAddress")]
        #[serde(default)]
        system_address: Option<u64>,
    },

    CarrierJump {
        timestamp: String,
        #[serde(rename = "StarSystem")]
        star_system: String,
        #[serde(rename = "Docked")]
        #[serde(default)]
        docked: bool,
    },

    SupercruiseEntry {
        timestamp: String,
        #[serde(rename = "StarSystem")]
        #[serde(default)]
        star_system: Option<String>,
    },

    SupercruiseExit {
        timestamp: String,
        #[serde(rename = "StarSystem")]
        #[serde(default)]
        star_system: Option<String>,
        #[serde(rename = "Body")]
        #[serde(default)]
        body: Option<String>,
        #[serde(rename = "BodyType")]
        #[serde(default)]
        body_type: Option<String>,
    },

    ApproachBody {
        timestamp: String,
        #[serde(rename = "StarSystem")]
        #[serde(default)]
        star_system: Option<String>,
        #[serde(rename = "Body")]
        body: String,
    },

    LeaveBody {
        timestamp: String,
        #[serde(rename = "StarSystem")]
        #[serde(default)]
        star_system: Option<String>,
        #[serde(rename = "Body")]
        #[serde(default)]
        body: Option<String>,
    },

    // ===== Docking Events =====
    Docked {
        timestamp: String,
        #[serde(rename = "StationName")]
        station_name: String,
        #[serde(rename = "StationType")]
        #[serde(default)]
        station_type: Option<String>,
        #[serde(rename = "StarSystem")]
        #[serde(default)]
        star_system: Option<String>,
    },

    Undocked {
        timestamp: String,
        #[serde(rename = "StationName")]
        #[serde(default)]
        station_name: Option<String>,
    },

    // ===== Ship Events =====
    Loadout {
        timestamp: String,
        #[serde(rename = "Ship")]
        ship: String,
        #[serde(rename = "ShipName")]
        #[serde(default)]
        ship_name: Option<String>,
        #[serde(rename = "ShipIdent")]
        #[serde(default)]
        ship_ident: Option<String>,
    },

    // ===== Landing Events =====
    Touchdown {
        timestamp: String,
        #[serde(rename = "PlayerControlled")]
        #[serde(default)]
        player_controlled: bool,
        #[serde(rename = "OnPlanet")]
        #[serde(default)]
        on_planet: bool,
        #[serde(rename = "OnStation")]
        #[serde(default)]
        on_station: bool,
    },

    Liftoff {
        timestamp: String,
        #[serde(rename = "PlayerControlled")]
        #[serde(default)]
        player_controlled: bool,
    },

    // ===== SRV Events =====
    LaunchSRV {
        timestamp: String,
        #[serde(rename = "SRVType")]
        #[serde(default)]
        srv_type: Option<String>,
        #[serde(rename = "PlayerControlled")]
        #[serde(default)]
        player_controlled: bool,
    },

    DockSRV {
        timestamp: String,
    },

    // ===== On Foot Events =====
    Disembark {
        timestamp: String,
        #[serde(rename = "OnStation")]
        #[serde(default)]
        on_station: bool,
        #[serde(rename = "OnPlanet")]
        #[serde(default)]
        on_planet: bool,
        #[serde(rename = "Taxi")]
        #[serde(default)]
        taxi: bool,
        #[serde(rename = "SRV")]
        #[serde(default)]
        srv: bool,
    },

    Embark {
        timestamp: String,
        #[serde(rename = "OnStation")]
        #[serde(default)]
        on_station: bool,
        #[serde(rename = "OnPlanet")]
        #[serde(default)]
        on_planet: bool,
        #[serde(rename = "Taxi")]
        #[serde(default)]
        taxi: bool,
        #[serde(rename = "SRV")]
        #[serde(default)]
        srv: bool,
        #[serde(rename = "StationName")]
        #[serde(default)]
        station_name: Option<String>,
    },

    SuitLoadout {
        timestamp: String,
        #[serde(rename = "SuitName")]
        #[serde(default)]
        suit_name: Option<String>,
        #[serde(rename = "SuitName_Localised")]
        #[serde(default)]
        suit_name_localised: Option<String>,
    },

    DropShipDeploy {
        timestamp: String,
        #[serde(rename = "OnStation")]
        #[serde(default)]
        on_station: bool,
        #[serde(rename = "OnPlanet")]
        #[serde(default)]
        on_planet: bool,
    },

    // ===== Multicrew & Wing =====
    WingJoin {
        timestamp: String,
    },

    WingAdd {
        timestamp: String,
        #[serde(rename = "Name")]
        #[serde(default)]
        name: Option<String>,
    },

    WingLeave {
        timestamp: String,
    },

    JoinACrew {
        timestamp: String,
        #[serde(rename = "Captain")]
        #[serde(default)]
        captain: Option<String>,
    },

    QuitACrew {
        timestamp: String,
    },

    EndCrewSession {
        timestamp: String,
    },

    // ===== Powerplay =====
    Powerplay {
        timestamp: String,
        #[serde(rename = "Power")]
        power: String,
    },

    PowerplayJoin {
        timestamp: String,
        #[serde(rename = "Power")]
        power: String,
    },

    PowerplayDefect {
        timestamp: String,
        #[serde(rename = "FromPower")]
        #[serde(default)]
        from_power: Option<String>,
        #[serde(rename = "ToPower")]
        to_power: String,
    },

    PowerplayLeave {
        timestamp: String,
        #[serde(rename = "Power")]
        #[serde(default)]
        power: Option<String>,
    },

    // ===== Music (for main menu detection) =====
    Music {
        timestamp: String,
        #[serde(rename = "MusicTrack")]
        music_track: String,
    },

    // ===== Continued (journal file switch) =====
    Continued {
        timestamp: String,
        #[serde(rename = "Part")]
        #[serde(default)]
        part: Option<u32>,
    },

    // ===== Unknown event - catch-all for forward compatibility =====
    /// Represents any event we don't explicitly handle.
    /// The raw JSON is preserved for debugging.
    #[serde(other)]
    Unknown,
}

impl JournalEvent {
    /// Get the timestamp of the event, if available
    pub fn timestamp(&self) -> Option<&str> {
        match self {
            JournalEvent::Fileheader { timestamp, .. } => Some(timestamp),
            JournalEvent::LoadGame { timestamp, .. } => Some(timestamp),
            JournalEvent::Shutdown { timestamp, .. } => Some(timestamp),
            JournalEvent::Location { timestamp, .. } => Some(timestamp),
            JournalEvent::FSDJump { timestamp, .. } => Some(timestamp),
            JournalEvent::CarrierJump { timestamp, .. } => Some(timestamp),
            JournalEvent::SupercruiseEntry { timestamp, .. } => Some(timestamp),
            JournalEvent::SupercruiseExit { timestamp, .. } => Some(timestamp),
            JournalEvent::ApproachBody { timestamp, .. } => Some(timestamp),
            JournalEvent::LeaveBody { timestamp, .. } => Some(timestamp),
            JournalEvent::Docked { timestamp, .. } => Some(timestamp),
            JournalEvent::Undocked { timestamp, .. } => Some(timestamp),
            JournalEvent::Loadout { timestamp, .. } => Some(timestamp),
            JournalEvent::Touchdown { timestamp, .. } => Some(timestamp),
            JournalEvent::Liftoff { timestamp, .. } => Some(timestamp),
            JournalEvent::LaunchSRV { timestamp, .. } => Some(timestamp),
            JournalEvent::DockSRV { timestamp, .. } => Some(timestamp),
            JournalEvent::Disembark { timestamp, .. } => Some(timestamp),
            JournalEvent::Embark { timestamp, .. } => Some(timestamp),
            JournalEvent::SuitLoadout { timestamp, .. } => Some(timestamp),
            JournalEvent::DropShipDeploy { timestamp, .. } => Some(timestamp),
            JournalEvent::WingJoin { timestamp, .. } => Some(timestamp),
            JournalEvent::WingAdd { timestamp, .. } => Some(timestamp),
            JournalEvent::WingLeave { timestamp, .. } => Some(timestamp),
            JournalEvent::JoinACrew { timestamp, .. } => Some(timestamp),
            JournalEvent::QuitACrew { timestamp, .. } => Some(timestamp),
            JournalEvent::EndCrewSession { timestamp, .. } => Some(timestamp),
            JournalEvent::Powerplay { timestamp, .. } => Some(timestamp),
            JournalEvent::PowerplayJoin { timestamp, .. } => Some(timestamp),
            JournalEvent::PowerplayDefect { timestamp, .. } => Some(timestamp),
            JournalEvent::PowerplayLeave { timestamp, .. } => Some(timestamp),
            JournalEvent::Music { timestamp, .. } => Some(timestamp),
            JournalEvent::Continued { timestamp, .. } => Some(timestamp),
            JournalEvent::Unknown => None,
        }
    }

    /// Get the event type name
    pub fn event_type(&self) -> &'static str {
        match self {
            JournalEvent::Fileheader { .. } => "Fileheader",
            JournalEvent::LoadGame { .. } => "LoadGame",
            JournalEvent::Shutdown { .. } => "Shutdown",
            JournalEvent::Location { .. } => "Location",
            JournalEvent::FSDJump { .. } => "FSDJump",
            JournalEvent::CarrierJump { .. } => "CarrierJump",
            JournalEvent::SupercruiseEntry { .. } => "SupercruiseEntry",
            JournalEvent::SupercruiseExit { .. } => "SupercruiseExit",
            JournalEvent::ApproachBody { .. } => "ApproachBody",
            JournalEvent::LeaveBody { .. } => "LeaveBody",
            JournalEvent::Docked { .. } => "Docked",
            JournalEvent::Undocked { .. } => "Undocked",
            JournalEvent::Loadout { .. } => "Loadout",
            JournalEvent::Touchdown { .. } => "Touchdown",
            JournalEvent::Liftoff { .. } => "Liftoff",
            JournalEvent::LaunchSRV { .. } => "LaunchSRV",
            JournalEvent::DockSRV { .. } => "DockSRV",
            JournalEvent::Disembark { .. } => "Disembark",
            JournalEvent::Embark { .. } => "Embark",
            JournalEvent::SuitLoadout { .. } => "SuitLoadout",
            JournalEvent::DropShipDeploy { .. } => "DropShipDeploy",
            JournalEvent::WingJoin { .. } => "WingJoin",
            JournalEvent::WingAdd { .. } => "WingAdd",
            JournalEvent::WingLeave { .. } => "WingLeave",
            JournalEvent::JoinACrew { .. } => "JoinACrew",
            JournalEvent::QuitACrew { .. } => "QuitACrew",
            JournalEvent::EndCrewSession { .. } => "EndCrewSession",
            JournalEvent::Powerplay { .. } => "Powerplay",
            JournalEvent::PowerplayJoin { .. } => "PowerplayJoin",
            JournalEvent::PowerplayDefect { .. } => "PowerplayDefect",
            JournalEvent::PowerplayLeave { .. } => "PowerplayLeave",
            JournalEvent::Music { .. } => "Music",
            JournalEvent::Continued { .. } => "Continued",
            JournalEvent::Unknown => "Unknown",
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_fileheader() {
        let json = r#"{"timestamp":"2024-01-15T10:30:00Z","event":"Fileheader","gameversion":"4.0.0.1","build":"r123456","language":"English"}"#;
        let event: JournalEvent = serde_json::from_str(json).unwrap();
        assert!(matches!(event, JournalEvent::Fileheader { .. }));
    }

    #[test]
    fn test_parse_unknown_event() {
        let json = r#"{"timestamp":"2024-01-15T10:30:00Z","event":"SomeFutureEvent","data":123}"#;
        let event: JournalEvent = serde_json::from_str(json).unwrap();
        assert!(matches!(event, JournalEvent::Unknown));
    }

    #[test]
    fn test_parse_location_with_missing_optional_fields() {
        let json = r#"{"timestamp":"2024-01-15T10:30:00Z","event":"Location","StarSystem":"Sol","Docked":false}"#;
        let event: JournalEvent = serde_json::from_str(json).unwrap();
        if let JournalEvent::Location { star_system, body, .. } = event {
            assert_eq!(star_system, "Sol");
            assert!(body.is_none());
        } else {
            panic!("Expected Location event");
        }
    }
}
