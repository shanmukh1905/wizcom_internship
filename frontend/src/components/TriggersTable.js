import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import config from "../config";

const TriggersTable = ({ triggers, fetchTriggers }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editingTrigger, setEditingTrigger] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [selectedHNIs, setSelectedHNIs] = useState([]); // State for selected HNI values
  const [uniqueHNIs, setUniqueHNIs] = useState([]); // State for unique HNI values
  const [isFilterVisible, setIsFilterVisible] = useState(false); // State to control filter visibility
  const [currentPage, setCurrentPage] = useState(1); // State for current page
  const [rowsPerPage] = useState(20); // Number of rows per page
  const [searchTerm, setSearchTerm] = useState(""); // State for search term

  const userId = localStorage.getItem("user_id");

  const filterRef = useRef(); // Reference for the filter window
  const columnRef = useRef(); // Reference for the "HNI" column header

  useEffect(() => {
    // Get unique HNI values from triggers, handle null as a special case
    const hnIs = [...new Set(triggers.map((trigger) => trigger.HNI !== null ? trigger.HNI : "NULL"))];
    setUniqueHNIs(hnIs);
    setSelectedHNIs(hnIs); // Initially, select all HNI values, including "NULL"
  }, [triggers]);

  const handleDelete = async (triggerId) => {
    const isConfirmed = window.confirm("Are you sure you want to delete this trigger?");
    if (!isConfirmed) return;

    setIsDeleting(true);
    try {
      await axios.delete(config.apiUrl+`/active-triggers/${userId}/${triggerId}`);
      fetchTriggers(); // Refresh the list after deletion
      alert("Trigger deleted successfully");
    } catch (error) {
      console.error("Error deleting trigger", error);
      alert("Failed to delete trigger. Please try again.");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleEdit = (trigger) => {
    setEditingTrigger({ ...trigger }); // Make a copy to edit
    setIsEditing(true);
  };

  const handleUpdate = async (updatedData) => {
    try {
      await axios.put(
        config.apiUrl+`/active-triggers/${userId}/${editingTrigger.TRIGGER_ID}`,
        updatedData
      );
      alert("Trigger updated successfully");
      fetchTriggers(); // Refresh the list after update
      setIsEditing(false);
      setEditingTrigger(null);
    } catch (error) {
      console.error("Error updating trigger", error);
      alert("Failed to update trigger. Please try again.");
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditingTrigger(null);
  };

  const handleHNICheckboxChange = (event) => {
    const { value, checked } = event.target;
    if (checked) {
      setSelectedHNIs((prev) => [...prev, value]);
    } else {
      setSelectedHNIs((prev) => prev.filter((hni) => hni !== value));
    }
  };

  const handleDeselectAll = () => {
    setSelectedHNIs([]); // Clear selected HNIs, unchecking all checkboxes
  };

  const handleSelectAll = () => {
    setSelectedHNIs(uniqueHNIs); // Select all HNIs
  };

  const handleStatusChange = (status) => {
    setEditingTrigger((prev) => ({
      ...prev,
      STATUS: status,
    }));
  };

  const filteredTriggers = triggers
    .filter((trigger) =>
      selectedHNIs.includes(trigger.HNI !== null ? trigger.HNI : "NULL")
    )
    .filter((trigger) =>
      trigger.SYMBOL.toLowerCase().includes(searchTerm.toLowerCase())
    ); // Filter by symbol based on search term

  // Calculate index of the first and last item based on current page and rows per page
  const indexOfLastTrigger = currentPage * rowsPerPage;
  const indexOfFirstTrigger = indexOfLastTrigger - rowsPerPage;
  const currentTriggers = filteredTriggers.slice(indexOfFirstTrigger, indexOfLastTrigger);

  // Open filter window when the "HNI" column header is clicked
  const handleColumnClick = () => {
    setIsFilterVisible((prev) => !prev); // Toggle visibility
  };

  // Close filter window if clicked outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (filterRef.current && !filterRef.current.contains(event.target) && columnRef.current && !columnRef.current.contains(event.target)) {
        setIsFilterVisible(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  
  const totalPages = Math.ceil(filteredTriggers.length / rowsPerPage); // Calculate total number of pages

  return (
    <div>
      {isDeleting && <p>Deleting trigger, please wait...</p>}

      {/* Floating filter window */}
      {isFilterVisible && (
        <div
          ref={filterRef}
          className="filter-container"
          id="filter-hni-container"
        >
          <h3 className="filter-heading" id="filter-heading">
            Filter by HNI:
          </h3>
          
          {/* Deselect All and Select All buttons */}
          <button onClick={handleDeselectAll} className="filter-action-btn">Deselect All</button>
          <button onClick={handleSelectAll} className="filter-action-btn">Select All</button>
          
          {uniqueHNIs.map((hni) => (
            <label key={hni} className="filter-label" htmlFor={`checkbox-${hni}`}>
              <input
                type="checkbox"
                value={hni}
                id={`checkbox-${hni}`}
                className="filter-checkbox"
                checked={selectedHNIs.includes(hni)}
                onChange={handleHNICheckboxChange}
              />
              {hni === "NULL" ? "Null" : hni} {/* Display "Null" for null values */}
            </label>
          ))}
        </div>
      )}

      {currentTriggers.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th scope="col">
                Symbol
                <input
                  type="text"
                  placeholder="Search"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-bar"
                />
              </th>
              <th scope="col">Series</th>
              <th scope="col" ref={columnRef} onClick={handleColumnClick}>
                HNI {/* The filter applies to the HNI column */}
              </th>
              <th scope="col">LOP</th>
              <th scope="col">BOP</th>
              <th scope="col">Deviation</th>
              <th scope="col">Comments</th>
              <th scope="col">Status</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {currentTriggers.map((trigger) => (
              <tr key={trigger.TRIGGER_ID}>
                <td>{trigger.SYMBOL}</td>
                <td>{trigger.SERIES}</td>
                <td>{trigger.HNI}</td>
                <td>
                  {isEditing && editingTrigger.TRIGGER_ID === trigger.TRIGGER_ID ? (
                    <input
                      type="text"
                      value={editingTrigger.LOP}
                      onChange={(e) =>
                        setEditingTrigger({
                          ...editingTrigger,
                          LOP: e.target.value,
                        })
                      }
                    />
                  ) : (
                    trigger.LOP
                  )}
                </td>
                <td>
                  {isEditing && editingTrigger.TRIGGER_ID === trigger.TRIGGER_ID ? (
                    <input
                      type="text"
                      value={editingTrigger.BOP}
                      onChange={(e) =>
                        setEditingTrigger({
                          ...editingTrigger,
                          BOP: e.target.value,
                        })
                      }
                    />
                  ) : (
                    trigger.BOP
                  )}
                </td>
                <td>
                  {isEditing && editingTrigger.TRIGGER_ID === trigger.TRIGGER_ID ? (
                    <input
                      type="text"
                      value={editingTrigger.DEVIATION}
                      onChange={(e) =>
                        setEditingTrigger({
                          ...editingTrigger,
                          DEVIATION: e.target.value,
                        })
                      }
                    />
                  ) : (
                    trigger.DEVIATION
                  )}
                </td>
                <td>
                  {isEditing && editingTrigger.TRIGGER_ID === trigger.TRIGGER_ID ? (
                    <input
                      type="text"
                      value={editingTrigger.COMMENTS}
                      onChange={(e) =>
                        setEditingTrigger({
                          ...editingTrigger,
                          COMMENTS: e.target.value,
                        })
                      }
                    />
                  ) : (
                    trigger.COMMENTS
                  )}
                </td>
                <td>
                  {isEditing && editingTrigger.TRIGGER_ID === trigger.TRIGGER_ID ? (
                    <select
                      value={editingTrigger.STATUS}
                      onChange={(e) => handleStatusChange(e.target.value)}
                    >
                      <option value="ACTIVE">ACTIVE</option>
                      <option value="INACTIVE">INACTIVE</option>
                    </select>
                  ) : (
                    trigger.STATUS
                  )}
                </td>
                <td>
                  {isEditing && editingTrigger.TRIGGER_ID === trigger.TRIGGER_ID ? (
                    <>
                      <button
                        onClick={() => handleUpdate(editingTrigger)}
                        aria-label={`Save trigger for ${trigger.SYMBOL}`}
                      >
                        Save
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        aria-label={`Cancel edit for ${trigger.SYMBOL}`}
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={() => handleEdit(trigger)}
                        aria-label={`Edit trigger for ${trigger.SYMBOL}`}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(trigger.TRIGGER_ID)}
                        aria-label={`Delete trigger for ${trigger.SYMBOL}`}
                      >
                        Delete
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No active triggers found.</p>
      )}

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
  );
};

export default TriggersTable;
