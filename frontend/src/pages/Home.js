import React, { useState} from 'react';
import toast from 'react-hot-toast';
import {Link, useNavigate} from 'react-router-dom';

const Home = () => {
    const apiUrl = process.env.REACT_APP_BACKEND_URL;

    const navigate = useNavigate();

    const [roomId, setRoomId] = useState('');
    const [username, setUsername] = useState('');

    const createNewRoom = async (e) => {
        e.preventDefault();
        const data = {
            document_id: "Untitled",
            name: "New Session",
            max_participants: 10,
            is_public: true,
            session_timeout: 60
        };

        try {
          const response = await fetch(
            `${process.env.REACT_APP_BACKEND_URL}/api/sessions/`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify(data),
            }
          );

          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }

          const result = await response.json();
          toast.success("Created a new room");
          setRoomId(result.session_id);
        } catch (error) {
          toast.error("Failed to create session");
          console.error("Fetch error:", error);
        }
    };

    const joinRoom = async () => {
        if (!roomId || !username) {
            toast.error('Room ID & Username is required');
            return;
        }

        try {
          const response = await fetch(
            `${apiUrl}/api/sessions/join?roomId=${roomId}`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ 'user_id':username }),
            }
          );

          if (!response.ok) {
            const errorData = await response.json();
            toast.error("Failed to join room");
            return;
          }

          const result = await response.json();
          navigate(`/editor/${roomId}`, {
            state: { username },
          });
        } catch (error) {
          toast.error("Error occurred while trying to join the room");
        }
    };

    const handleInputEnter = (e) => {
        if (e.code === 'Enter') {
            joinRoom();
        }
    };

    return (
        <div className="homePageWrapper">
            <div className="formWrapper">
                <img
                    className="homePageLogo"
                    src="/logo.png"
                    alt="code-sync-logo"
                />
                <h4 className="mainLabel">Generate new room or paste invitation ROOM ID</h4>
                <div className="inputGroup">
                    <input
                        type="text"
                        className="inputBox"
                        placeholder="ROOM ID"
                        onChange={(e) => setRoomId(e.target.value)}
                        value={roomId}
                        onKeyUp={handleInputEnter}
                    />
                    <input
                        type="text"
                        className="inputBox"
                        placeholder="USERNAME"
                        onChange={(e) => setUsername(e.target.value)}
                        value={username}
                        onKeyUp={handleInputEnter}
                    />
                    <button className="btn joinBtn" onClick={joinRoom}>
                        Join
                    </button>
                    <span className="createInfo">
                        If you don't have an invite then create &nbsp;
                        <Link
                            onClick={createNewRoom}
                            href=""
                            className="createNewBtn"
                        >
                            new room
                        </Link>
                    </span>
                </div>
            </div>
        </div>
    );
};

export default Home;