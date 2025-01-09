import React, { useState, useEffect } from "react";
import axios from "axios";
import * as XLSX from "xlsx";
import TriggersTable from "../components/TriggersTable";
import config from "../config";

const ActiveTriggersPage = () => {
  const [alltriggers, getTriggers] = useState([]);
  const [triggers, setTriggers] = useState([]);
  const [file, setFile] = useState(null);
  const [uploadError, setUploadError] = useState("");
  
  const [newTrigger, setNewTrigger] = useState({
    symbol: "",
    series: "",
    lop: "",
    bop: "",
    deviation: "",
    comments: "",
    status: "Active",
  });
  const [symbols, setSymbols] = useState([]);
  const [series, setSeries] = useState([]);
  const [loading, setLoading] = useState(true);

  const userId = localStorage.getItem("user_id");

  const fetchTriggers = async () => {
    try {
      const response = await axios.get(config.apiUrl+`/active-triggers/${userId}`);
      setTriggers(response.data);
    } catch (error) {
      console.error("Error fetching triggers", error);
    }
  };

  const fetchSymbolsAndSeries = async () => {
    try {
      const [symbolsResponse, seriesResponse] = await Promise.all([
        axios.get("http://127.0.0.1:5000/active-triggers/symbols"),
        axios.get("http://127.0.0.1:5000/active-triggers/series"),
      ]);
      setSymbols(symbolsResponse.data);
      setSeries(seriesResponse.data);
    } catch (error) {
      console.error("Error fetching symbols/series", error);
    }
  };

  const fetchAllTriggers = async () => {
    try {
      const response = await axios.get(config.apiUrl+`/all-triggers/${userId}`);
      getTriggers(response.data);
    } catch (error) {
      console.error("Error fetching inactive triggers", error);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        if (userId) {
          await Promise.all([fetchTriggers(), fetchSymbolsAndSeries(), fetchAllTriggers()]);
        }
      } catch (error) {
        console.error("Error fetching data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [userId]);

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setNewTrigger((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddTrigger = async (e) => {
    e.preventDefault();

    const trimmedSymbol = newTrigger.symbol.trim();
    const trimmedSeries = newTrigger.series.trim();
    const triggerId = `${trimmedSymbol}${trimmedSeries}`;

    if (isNaN(newTrigger.deviation)) {
      alert("Deviation must be a valid number!");
      return;
    }

    try {
      const payload = {
        trigger_id: triggerId,
        symbol: trimmedSymbol,
        series: trimmedSeries,
        lop: newTrigger.lop || null,
        bop: newTrigger.bop || null,
        deviation: parseFloat(newTrigger.deviation),
        comments: newTrigger.comments || "",
        status: newTrigger.status,
      };

      await axios.post(config.apiUrl+`/active-triggers/${userId}`, payload);

      alert("Trigger added successfully");
      setNewTrigger({
        symbol: "",
        series: "",
        lop: "",
        bop: "",
        deviation: "",
        comments: "",
        status: "Active",
      });
      fetchTriggers();
    } catch (error) {
      console.error("Error adding trigger", error);
      alert("Failed to add trigger. Please check your inputs.");
    }
  };

  const handleFileUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);
    try {
      await axios.post(config.apiUrl+`/upload-triggers-file/${userId}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert("File uploaded successfully!");
      fetchTriggers();
    } catch (error) {
      setUploadError("Error uploading file. Please try again.");
      console.error("Error uploading file:", error);
    }
  };

  const exportToExcel = () => {
    fetchAllTriggers(); // Ensure all triggers are fetched before exporting
    if (alltriggers.length === 0) {
      alert("No data available to export!");
      return;
    }

    // Define the desired column order
    const columnsOrder = [
      "SYMBOL", 
      "SERIES", 
      "HNI",
      "LOP",
      "BOP",
      "DEVIATION",
      "COMMENTS",
      "STATUS",
    ];

    // Format the triggers to ensure the correct column order
    const formattedTriggers = alltriggers.map((trigger) =>
      columnsOrder.reduce((obj, key) => {
        obj[key] = trigger[key];
        return obj;
      }, {})
    );

    // Create the worksheet with the custom column order
    const ws = XLSX.utils.json_to_sheet(formattedTriggers);

    // Add the header row explicitly
    XLSX.utils.sheet_add_aoa(ws, [columnsOrder], { origin: "A1" });

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "All Triggers");

    XLSX.writeFile(wb, "All_Triggers.xlsx");
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div id="active-triggers-page" className="page-container">
      <center>
        <h2 className="form-title">Add New Trigger</h2>
        <form id="trigger-form" className="form-container" onSubmit={handleAddTrigger}>
          <div className="form-group">
            <input
              type="text"
              name="symbol"
              list="symbols-list"
              value={newTrigger.symbol}
              onChange={handleFormChange}
              placeholder="Symbol"
              required
              className="form-input"
            />
            <datalist id="symbols-list">
              {symbols.map((symbol, index) => (
                <option key={index} value={symbol} />
              ))}
            </datalist>
          </div>
          <div className="form-group">
            <input
              type="text"
              name="series"
              list="series-list"
              value={newTrigger.series}
              onChange={handleFormChange}
              placeholder="Series"
              required
              className="form-input"
            />
            <datalist id="series-list">
              {series.map((series, index) => (
                <option key={index} value={series} />
              ))}
            </datalist>
          </div>
          <div className="form-group">
            <input
              type="number"
              name="lop"
              value={newTrigger.lop}
              onChange={handleFormChange}
              placeholder="LOP"
              className="form-input"
            />
          </div>
          <div className="form-group">
            <input
              type="number"
              name="bop"
              value={newTrigger.bop}
              onChange={handleFormChange}
              placeholder="BOP"
              className="form-input"
            />
          </div>
          <div className="form-group">
            <input
              type="text"
              name="deviation"
              value={newTrigger.deviation}
              onChange={handleFormChange}
              placeholder="Deviation"
              required
              className="form-input"
            />
          </div>
          <div className="form-group">
            <input
              type="text"
              name="comments"
              value={newTrigger.comments}
              onChange={handleFormChange}
              placeholder="Comments"
              className="form-input"
            />
          </div>
          <div className="form-group">
            <select
              name="status"
              value={newTrigger.status}
              onChange={handleFormChange}
              className="form-select"
            >
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
            </select>
          </div>
          <button type="submit" className="form-button">
            Add Trigger
          </button>
        </form>
      
        <div className="top-controls">
          {/* Excel File Upload */}
          <div className="file-upload-container">
            <h3 className="form-title">Upload Triggers using Excel File</h3>
            <input
              type="file"
              accept=".xlsx,.xls"
              onChange={(e) => setFile(e.target.files[0])}
              className="form-input-small"
            />
            <button onClick={handleFileUpload} className="form-button">
              Upload Excel File
            </button>
          </div>

          {/* Export to Excel Section */}
          <div className="export-section">
            <h2>Export All Triggers</h2>
            <button onClick={exportToExcel} className="export-button">
              Export as Excel
            </button>
          </div>
        </div>

        <TriggersTable
          className="triggers-table"
          triggers={triggers}
          userId={userId}
          fetchTriggers={fetchTriggers}
        />
      </center>
    </div>
  );
};

export default ActiveTriggersPage;
