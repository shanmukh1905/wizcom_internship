import React, { useState, useEffect } from "react";
import axios from "axios";
import * as XLSX from "xlsx"; // Import xlsx library
import config from "../config";

const HNIDetailsPage = () => {
  const [hniDetails, setHNIDetails] = useState([]);
  const [newHNI, setNewHNI] = useState({ SYMBOL: "", COMPANY_NAME: "", HNI_DETAILS: "" });
  const [editHNI, setEditHNI] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage] = useState(20);
  const [file, setFile] = useState(null);

  const fetchHNIDetails = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/hni-details");
      setHNIDetails(response.data);
    } catch (error) {
      console.error("Error fetching HNI details:", error);
    }
  };

  useEffect(() => {
    fetchHNIDetails();
  }, []);

  const handleFileUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);
    try {
      await axios.post("http://127.0.0.1:5000/upload-hni-file", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert("File uploaded successfully!");
      fetchHNIDetails();
    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  const handleAddHNI = async () => {
    try {
      await axios.post("http://127.0.0.1:5000/hni-details", newHNI);
      setNewHNI({ SYMBOL: "", COMPANY_NAME: "", HNI_DETAILS: "" });
      fetchHNIDetails();
    } catch (error) {
      console.error("Error adding HNI:", error);
    }
  };

  const handleEditHNI = async (symbol, hniDetails) => {
    try {
      await axios.put(config.apiUrl+`/hni-details/${symbol}`, {
        COMPANY_NAME: editHNI.COMPANY_NAME,
        HNI_DETAILS: editHNI.HNI_DETAILS,
        CURRENT_HNI_DETAILS: hniDetails,
      });
      setEditHNI(null);
      fetchHNIDetails();
    } catch (error) {
      console.error("Error editing HNI:", error);
    }
  };

  const handleDeleteHNI = async (symbol, hniDetails) => {
    try {
      await axios.delete(config.apiUrl+`/hni-details/${symbol}`, {
        data: { HNI_DETAILS: hniDetails },
      });
      fetchHNIDetails();
    } catch (error) {
      console.error("Error deleting HNI:", error);
    }
  };

  const handleEditButtonClick = (hni) => {
    setEditHNI({
      SYMBOL: hni.SYMBOL,
      COMPANY_NAME: hni.COMPANY_NAME,
      HNI_DETAILS: hni.HNI_DETAILS,
    });
  };

  const filteredHNI = hniDetails.filter(
    (hni) =>
      hni.SYMBOL.toLowerCase().includes(searchQuery.toLowerCase()) ||
      hni.HNI_DETAILS.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const indexOfLastHNI = currentPage * rowsPerPage;
  const indexOfFirstHNI = indexOfLastHNI - rowsPerPage;
  const currentHNIs = filteredHNI.slice(indexOfFirstHNI, indexOfLastHNI);
  const totalPages = Math.ceil(filteredHNI.length / rowsPerPage);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  // Export HNI details to Excel
  const exportToExcel = () => {
    if (hniDetails.length === 0) {
      alert("No data available to export!");
      return;
    }

    // Define the columns order
    const columnsOrder = ["SYMBOL", "COMPANY_NAME", "HNI_DETAILS"];

    // Format the HNI data to match the order of columns
    const formattedHNI = hniDetails.map((hni) =>
      columnsOrder.reduce((obj, key) => {
        obj[key] = hni[key];
        return obj;
      }, {})
    );

    // Create the worksheet
    const ws = XLSX.utils.json_to_sheet(formattedHNI);

    // Add the headers explicitly
    XLSX.utils.sheet_add_aoa(ws, [columnsOrder], { origin: "A1" });

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "HNIDetails");

    // Write the Excel file
    XLSX.writeFile(wb, "HNIDetails.xlsx");
  };

  return (
    <div id="hni-details-page" className="page-container">
      <center>
        <h3 className="form-title">Add New HNI</h3>
        <div className="form-container">
          <div className="form-group">
            <input
              type="text"
              placeholder="Symbol"
              value={newHNI.SYMBOL}
              onChange={(e) => setNewHNI({ ...newHNI, SYMBOL: e.target.value })}
              className="form-input"
            />
          </div>
          <div className="form-group">
            <input
              type="text"
              placeholder="Company Name"
              value={newHNI.COMPANY_NAME}
              onChange={(e) => setNewHNI({ ...newHNI, COMPANY_NAME: e.target.value })}
              className="form-input"
            />
          </div>
          <div className="form-group">
            <input
              type="text"
              placeholder="HNI Details"
              value={newHNI.HNI_DETAILS}
              onChange={(e) => setNewHNI({ ...newHNI, HNI_DETAILS: e.target.value })}
              className="form-input"
            />
          </div>
          <button onClick={handleAddHNI} className="form-button">
            Add HNI
          </button>
        </div>
        <div className="top-controls">
          {/* Excel File Upload */}
          <div className="file-upload-container">
            <h3 className="form-title">Upload HNI using Excel File</h3>
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
            <h3>Export HNI Details</h3>
            <button onClick={exportToExcel} className="form-button">
              Export as Excel
            </button>
          </div>
        </div>

        <h3 className="form-title">HNI Details</h3>
        {/* Search Input */}
        <div className="search-container">
          <input
            type="text"
            placeholder="Search by Symbol or HNI Details"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="form-input-small"
          />
        </div>

        {/* Display HNI Details Table */}
        <table className="hni-details-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Company Name</th>
              <th>HNI Details</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {currentHNIs.map((hni) =>
              editHNI && editHNI.SYMBOL === hni.SYMBOL ? (
                <tr key={`${hni.SYMBOL}-${hni.HNI_DETAILS}`}>
                  <td>{hni.SYMBOL}</td>
                  <td>
                    <input
                      type="text"
                      value={editHNI.COMPANY_NAME}
                      onChange={(e) => setEditHNI({ ...editHNI, COMPANY_NAME: e.target.value })}
                      className="form-input"
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      value={editHNI.HNI_DETAILS}
                      onChange={(e) => setEditHNI({ ...editHNI, HNI_DETAILS: e.target.value })}
                      className="form-input"
                    />
                  </td>
                  <td>
                    <button onClick={() => handleEditHNI(hni.SYMBOL, hni.HNI_DETAILS)}>Save</button>
                    <button onClick={() => setEditHNI(null)}>Cancel</button>
                  </td>
                </tr>
              ) : (
                <tr key={`${hni.SYMBOL}-${hni.HNI_DETAILS}`}>
                  <td>{hni.SYMBOL}</td>
                  <td>{hni.COMPANY_NAME}</td>
                  <td>{hni.HNI_DETAILS}</td>
                  <td>
                    <button onClick={() => handleEditButtonClick(hni)}>Edit</button>
                    <button onClick={() => handleDeleteHNI(hni.SYMBOL, hni.HNI_DETAILS)}>Delete</button>
                  </td>
                </tr>
              )
            )}
          </tbody>
        </table>

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
      </center>
    </div>
  );
};

export default HNIDetailsPage;
