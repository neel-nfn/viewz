import { useState, useEffect } from "react";
import { listChannels } from "../../services/channelService";

export default function ChannelSelector({ selectedChannelId, onChannelChange, loading = false }) {
  const [channels, setChannels] = useState([]);
  const [loadingChannels, setLoadingChannels] = useState(true);
  
  useEffect(() => {
    async function loadChannels() {
      try {
        const channelList = await listChannels();
        setChannels(channelList);
        
        // Persist last selected channel
        const lastSelected = localStorage.getItem("analytics_selected_channel");
        if (lastSelected && channelList.find(c => c.id === lastSelected)) {
          onChannelChange(lastSelected);
        } else if (channelList.length > 0 && !selectedChannelId) {
          onChannelChange(channelList[0].id);
        }
      } catch (error) {
        console.error("Error loading channels:", error);
      } finally {
        setLoadingChannels(false);
      }
    }
    
    loadChannels();
  }, []);
  
  const handleChange = (channelId) => {
    localStorage.setItem("analytics_selected_channel", channelId);
    onChannelChange(channelId);
  };
  
  if (loading || loadingChannels) {
    return (
      <div className="select select-bordered w-full max-w-xs animate-pulse">
        <option>Loading channels...</option>
      </div>
    );
  }
  
  if (channels.length === 0) {
    return null;
  }
  
  return (
    <select
      className="select select-bordered w-full max-w-xs"
      value={selectedChannelId || channels[0]?.id || ""}
      onChange={(e) => handleChange(e.target.value)}
    >
      {channels.map((channel) => (
        <option key={channel.id} value={channel.id}>
          {channel.title || channel.youtube_channel_id || "Unknown Channel"}
        </option>
      ))}
    </select>
  );
}

