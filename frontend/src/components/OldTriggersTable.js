import React, { useState, useEffect, useRef } from "react";

const OldTriggersTable = ({
  triggers,
  loading,
  title,
  filterColumn,
  sortColumn1,
  sortColumn2,
  showSortButton = true,
}) => {
  const [selectedFilters, setSelectedFilters] = useState([]);
  const [uniqueFilters, setUniqueFilters] = useState([]);
  const [isFilterVisible, setIsFilterVisible] = useState(false);
  const [sortOrder, setSortOrder] = useState("asc");
  const [sortedTriggers, setSortedTriggers] = useState([]);
  const filterRef = useRef();
  const columnRef = useRef();

  // Fetch unique filter options when triggers data changes
  useEffect(() => {
    const uniqueValues = [
      ...new Set(triggers.map((trigger) => trigger[filterColumn] || "NULL")),
    ];
    setUniqueFilters(uniqueValues);
    setSelectedFilters(uniqueValues); // Select all filters by default
  }, [triggers, filterColumn]);

  // Handle filter checkbox change
  const handleFilterChange = (event) => {
    const { value, checked } = event.target;
    if (checked) {
      setSelectedFilters((prev) => [...prev, value]);
    } else {
      setSelectedFilters((prev) => prev.filter((item) => item !== value));
    }
  };

  // Handle select/deselect all filters
  const handleSelectAll = () => setSelectedFilters(uniqueFilters);
  const handleDeselectAll = () => setSelectedFilters([]);

  // Handle sorting by selected column
  const handleSort = (column) => {
    const sorted = [...triggers].sort((a, b) => {
      const dateA = new Date(a[column]);
      const dateB = new Date(b[column]);

      // Ensure valid Date objects
      if (isNaN(dateA)) return 0;
      if (isNaN(dateB)) return 0;

      return sortOrder === "asc" ? dateA - dateB : dateB - dateA;
    });

    setSortedTriggers(sorted);
    setSortOrder(sortOrder === "asc" ? "desc" : "asc");
  };

  // Format date if column is Trigger Date or Trade Date
  const formatDate = (date) => {
    if (!date) return "N/A";
    return new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  // Open filter window on column click
  const handleColumnClick = () => setIsFilterVisible((prev) => !prev);

  // Close filter window if clicked outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        filterRef.current &&
        !filterRef.current.contains(event.target) &&
        columnRef.current &&
        !columnRef.current.contains(event.target)
      ) {
        setIsFilterVisible(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Initialize sorted triggers on page load
  useEffect(() => {
    setSortedTriggers(triggers);
  }, [triggers]);

  // Filter triggers based on selected filters
  const filteredTriggers = sortedTriggers.filter((trigger) =>
    selectedFilters.includes(trigger[filterColumn] || "NULL")
  );

  return (
    <div>
      <h3 className="page-title">{title}</h3>
      {isFilterVisible && (
        <div ref={filterRef} className="filter-container">
          <h3 className="filter-heading">Filter by {filterColumn}:</h3>
          <button className="filter-button" onClick={handleDeselectAll}>
            Deselect All
          </button>
          <button className="filter-button" onClick={handleSelectAll}>
            Select All
          </button>
          {uniqueFilters.map((value) => (
            <label key={value} className="filter-label">
              <input
                type="checkbox"
                value={value}
                checked={selectedFilters.includes(value)}
                onChange={handleFilterChange}
                className="filter-checkbox"
              />
              {value === "NULL" ? "Null" : value}
            </label>
          ))}
        </div>
      )}

      {/* Table */}
      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <center>
          <div className="table-container">
            <table className="old-triggers-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Series</th>
                  <th
                    ref={columnRef}
                    onClick={handleColumnClick}
                    className="filter-column"
                  >
                    {filterColumn} {/* Column with filter */}
                  </th>
                  <th>OPEN</th>
                  <th>LOW</th>
                  <th>HIGH</th>
                  <th>CLOSE</th>
                  <th>LOP</th>
                  <th>BOP</th>
                  <th>Deviation</th>
                  <th>Comments</th>
                  {showSortButton && (
                    <th>
                      Trade Date
                      <button
                        className="sort-button"
                        onClick={() => handleSort("TRADE_DATE")}
                      >
                        {sortOrder === "asc" ? "↓" : "↑"}
                      </button>
                    </th>
                  )}
                  {showSortButton && (
                    <th>
                      Trigger Date
                      <button
                        className="sort-button"
                        onClick={() => handleSort("TRIGGER_DATE")}
                      >
                        {sortOrder === "asc" ? "↓" : "↑"}
                      </button>
                    </th>
                  )}
                  <th>Type</th>
                </tr>
              </thead>
              <tbody>
                {filteredTriggers.map((trigger) => (
                  <tr key={trigger.UNIQUE_ID}>
                    <td>{trigger.SYMBOL}</td>
                    <td>{trigger.SERIES}</td>
                    <td>{trigger[filterColumn]}</td>
                    <td>{trigger.OPEN_PRICE}</td>
                    <td>{trigger.LOW_PRICE}</td>
                    <td>{trigger.HIGH_PRICE}</td>
                    <td>{trigger.CLOSE_PRICE}</td>
                    <td>{trigger.LOP}</td>
                    <td>{trigger.BOP}</td>
                    <td>{trigger.DEVIATION}</td>
                    <td>{trigger.COMMENTS}</td>
                    <td>{formatDate(trigger.TRADE_DATE)}</td>
                    <td>{formatDate(trigger.TRIGGER_DATE)}</td>
                    <td>{trigger.TYPE}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </center>
      )}
    </div>
  );
};

export default OldTriggersTable;
