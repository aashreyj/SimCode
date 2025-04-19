import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../login.css'; // or wherever your CSS is

const Login = () => {
    // const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');  // Change email to username
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (username === '' || password === '') {
            alert('Please fill in all fields');
            return;
        }

        try {
            const formData = new URLSearchParams();
            // formData.append('username', email);  // OAuth2 uses "username"
            formData.append('username', username);  // Use username for OAuth2
            formData.append('password', password);

            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Login failed');
            }

            const data = await response.json();
            console.log('Login success:', data);

            // You can save the token to localStorage if you want
            // localStorage.setItem('token', data.access_token);

            // Navigate to dashboard or home page
            navigate('/home');
        } catch (error) {
            console.error('Login error:', error.message);
            alert(error.message);
        }
    };


    return (
        <div className="homePageWrapper">
            <div className="formWrapper">
                <h2 className="mainLabel">Login</h2>
                <form onSubmit={handleSubmit} className="inputGroup">
                    <input
                        type="text"  // Changed this to text for username
                        className="inputBox"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}  // Updated state to username
                        required
                    />
                    <input
                        type="password"
                        className="inputBox"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <button type="submit" className="btn submitBtn">
                        Login
                    </button>
                </form>

                <p className="createInfo">
                    Don't have an account?{' '}
                    <a href="/signup" className="createNewBtn">
                        Sign up
                    </a>
                </p>
            </div>
        </div>
    );
};

export default Login;
