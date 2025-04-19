import React, {useState} from 'react';
import {v4 as uuidV4} from 'uuid';
import toast from 'react-hot-toast';
import {Link, useNavigate} from 'react-router-dom';

const Home = () => {
    const apiUrl = process.env.REACT_APP_BACKEND_URL;

    const navigate = useNavigate();

    const [roomId, setRoomId] = useState('');
    const [username, setUsername] = useState('');

    const createNewRoom = (e) => {
        e.preventDefault();
        const id = uuidV4();
        setRoomId(id);
        toast.success('Created a new room');
    };

    const joinRoom = async () => {
        if (!roomId || !username) {
            toast.error('ROOM ID & username is required');
            return;
        }

        try {
            const response = await fetch(`${apiUrl}/api/room-user-count?roomId=${roomId}`);
            if (!response.ok) throw new Error(`Error during fetch call: ${response.status}`)
            const json = await response.json();
            if (json.member_count < 8) {
                navigate(`/editor/${roomId}`, {
                    state: {
                        username,
                    },
                });
            }
            else {
                toast.error("Room is Full!");
                return;
            }
        } catch (error) {
            toast.error("Error occurred while trying to join the room");
            console.log(error);
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