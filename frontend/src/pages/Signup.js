import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import '../signup.css';

const Signup = () => {
    const navigate = useNavigate();
    const apiUrl = process.env.REACT_APP_BACKEND_URL;

    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [role, setRole] = useState(''); // <-- Add this line



    const handleSignup = async (e) => {
        e.preventDefault();

        if (!username || !email || !password) {
            toast.error('All fields are required');
            return;
        }

        if (password !== confirmPassword) {
            toast.error('Passwords do not match');
            return;
        }


        try {
            const response = await fetch(`${apiUrl}/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password, role_of_user: role }),
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || 'Signup failed');
            }

            toast.success('Signup successful!');
            navigate('/'); // redirect to login or home after signup
        } catch (error) {
            toast.error(error.message);
            console.error(error);
        }
    };

    return (
        <div className="signupPageWrapper">
            <div className="formWrapper">
                <h2 className="mainLabel">Create Account</h2>
                <form onSubmit={handleSignup} className="inputGroup">
                    <input
                        type="text"
                        className="inputBox"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <input
                        type="email"
                        className="inputBox"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <input
                        type="password"
                        className="inputBox"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <input
                        type="password"
                        className="inputBox"
                        placeholder="Confirm Password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}  // 🔧 was wrong
                    />
                    <select
                        className="inputBox"
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                    >
                        <option value="" disabled>Select Role</option>
                        <option value="host">Host</option>
                        <option value="editor">Editor</option>
                        <option value="viewer">Viewer</option>
                    </select>

                    <button type="submit" className="btn joinBtn">
                        Sign Up
                    </button>
                </form>
                <span className="createInfo">
                    Already have an account?&nbsp;
                    <a href="/" className="createNewBtn">
                        Log in
                    </a>
                </span>
            </div>
        </div>
    );
};

export default Signup;
