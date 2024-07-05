import React, { useState } from "react";
import axios from "axios";

axios.defaults.headers.post["Content-Type"] = "application/json";

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [docId, setDocId] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post(
      "http://localhost:8000/upload/",
      formData
    );
    setDocId(response.data.id);
  };

  const handleQuestionChange = (e) => {
    setQuestion(e.target.value);
  };

  const handleAsk = async () => {
    const formData = new FormData();
    formData.append("doc_id", docId);
    formData.append("question", question);

    const response = await axios.post("http://localhost:8000/ask/", formData);
    setAnswer(response.data.answer);
  };

  return (
    <>
      <div className="p-3 text-3xl text-center">
        <h2>PDF Question Answer</h2>
      </div>
      <div className="flex items-center p-3 border-8 border-cyan-400">
        <input className="" type="file" onChange={handleFileChange} />
        <button className="p-2 rounded-md bg-green-500" onClick={handleUpload}>
          Upload
        </button>
        {docId && (
          <div className="flex items-center p-3">
            <input
              className="p-3 bg-yellow-200 rounded-md"
              type="text"
              value={question}
              onChange={handleQuestionChange}
            />
            <button className="p-2 rounded-md bg-blue-500" onClick={handleAsk}>
              Ask Question
            </button>
            {answer && <p>Answer: {answer}</p>}
          </div>
        )}
      </div>
    </>
  );
};

export default FileUpload;
