import React, { useState, useEffect } from "react";
import axios from "axios";
import * as XLSX from "xlsx";
import OldTriggersTable from "../components/OldTriggersTable";
import config from "../config";

const PreviousTriggersPage = () => {
  const [previousTriggers, setPreviousTriggers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState("");
  const [dateLoading, setDateLoading] = useState(false); // For date submission loading

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage] = useState(20);

  useEffect(() => {
    const fetchPreviousTriggers = async () => {
      const userId = localStorage.getItem("user_id");
      if (!userId) {
        console.error("User ID not found in localStorage");
        return;
      }

      try {
        const response = await axios.get(config.apiUrl+`/previous-triggers/${userId}`);
        setPreviousTriggers(response.data);
      } catch (error) {
        console.error("Error fetching previous triggers", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPreviousTriggers();
  }, []);

  // Handle date selection change
  const handleDateChange = (e) => setSelectedDate(e.target.value);

  // Handle the on-demand run of the date
  const handleOnDemandRun = async (e) => {
    e.preventDefault();

    if (!selectedDate) {
      alert("Please select a date");
      return;
    }

    const userId = localStorage.getItem("user_id");
    if (!userId) {
      alert("User ID is missing");
      return;
    }

    setDateLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/submit-date", {
        date: selectedDate,
        user_id: userId,
      });

      if (response.data.status === "success") {
        alert(`Date ${response.data.received_date} submitted successfully!`);
        const fetchPreviousTriggers = async () => {
          try {
            const res = await axios.get(config.apiUrl+`/previous-triggers/${userId}`);
            setPreviousTriggers(res.data);
          } catch (error) {
            console.error("Error fetching previous triggers after submitting date", error);
          }
        };
        fetchPreviousTriggers();
      } else {
        alert("Failed to submit date. Please try again.");
      }
    } catch (error) {
      console.error("Error submitting the date:", error);
      alert("An error occurred while submitting the date. Please try again.");
    } finally {
      setDateLoading(false);
    }
  };

  // Export triggers to Excel (all columns dynamically)
  const exportToExcel = () => {
    if (previousTriggers.length === 0) {
      alert("No data available to export!");
      return;
    }
  
    // Define the desired column order
    const columnsOrder = [
      "SYMBOL", 
      "SERIES", 
      "HNI", 
      "OPEN_PRICE",
      "HIGH_PRICE",
      "LOW_PRICE",
      "CLOSE_PRICE",
      "LOP",
      "BOP",
      "DEVIATION",
      "COMMENTS",
      "TRADE_DATE", 
      "TRIGGER_DATE", 
      "TYPE"
    ];
  
    // Format the triggers to ensure the correct column order
    const formattedTriggers = previousTriggers.map((trigger) =>
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
    XLSX.utils.book_append_sheet(wb, ws, "PreviousTriggers");
  
    XLSX.writeFile(wb, "PreviousTriggers.xlsx");
  };
  

  // Pagination logic
  const indexOfLastTrigger = currentPage * rowsPerPage;
  const indexOfFirstTrigger = indexOfLastTrigger - rowsPerPage;
  const currentTriggers = previousTriggers.slice(indexOfFirstTrigger, indexOfLastTrigger);
  const totalPages = Math.ceil(previousTriggers.length / rowsPerPage);

  // Pagination control functions
  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <center>
      <div>
        <center>
        <div className="top-controls">
          {/* On Demand Run Section */}
          <div className="on-demand-run">
            <h2>On Demand Run</h2>
            <form onSubmit={handleOnDemandRun} className="date-picker-form">
              <label htmlFor="dateInput" className="date-picker-label">Select a Date:</label>
              <input
                type="date"
                id="dateInput"
                className="date-input"
                value={selectedDate}
                onChange={handleDateChange}
              />
              <button type="submit" className="date-picker-submit" disabled={dateLoading}>
                {dateLoading ? "Submitting..." : "Submit"}
              </button>
            </form>
          </div>

          {/* Export to Excel Section */}
          <div className="export-section">
            <h2>Export Data</h2>
            <button onClick={exportToExcel} className="export-button">
              Export as Excel
            </button>
          </div>
        </div>
        </center>


        {/* Old Triggers Table */}
        <div className="page-container">
          <OldTriggersTable
            triggers={currentTriggers}
            loading={loading}
            title="Alerts History"
            filterColumn="HNI"
            sortColumn1="TRADE_DATE"
            sortColumn2="TRIGGER_DATE"
            showSortButton={true}
          />
        </div>

        {/* Pagination Controls */}
        <div className="pagination-controls">
          <br />
          <button
            onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
          >
            Previous
          </button>
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
          >
            Next
          </button>
        </div>
      </div>
    </center>
  );
};

export default PreviousTriggersPage;
