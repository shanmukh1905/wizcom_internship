import React, { useState, useEffect } from "react";
import axios from "axios";
import TriggersTable from "../components/TriggersTable";
import config from "../config";

const InactiveTriggersPage = () => {
  const [triggers, setTriggers] = useState([]);
  const [loading, setLoading] = useState(true);

  const userId = localStorage.getItem("user_id");

  const fetchInactiveTriggers = async () => {
    try {
      const response = await axios.get(config.apiUrl+`/inactive-triggers/${userId}`);
      setTriggers(response.data);
    } catch (error) {
      console.error("Error fetching inactive triggers", error);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        if (userId) {
          await fetchInactiveTriggers();
        }
      } catch (error) {
        console.error("Error fetching data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [userId]);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div id="inactive-triggers-page" className="page-container">
      <center>
        <TriggersTable
          className="triggers-table"
          triggers={triggers}
          userId={userId}
          fetchTriggers={fetchInactiveTriggers}
        />
      </center>
    </div>
  );
};

export default InactiveTriggersPage;
