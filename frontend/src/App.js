import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Home from './pages/Home';
import { RecoilRoot } from "recoil";
import EditorPageContainer from './pages/EditorPageContainer';
import SignUp from './pages/Signup';
import Login from './pages/Login';
// import EditorPage from './pages/EditorPage';

function App() {

    return (
        <>
            <div>
                <Toaster
                    position="top-center"
                    toastOptions={{
                        success: {
                            theme: {
                                primary: '#4aed88',
                            },
                        },
                    }}
                ></Toaster>
            </div>
            <BrowserRouter>
                <RecoilRoot>
                    <Routes>
                        <Route path="/" element={<Login />}></Route>
                        <Route path="/Signup" element={<SignUp />}></Route>
                        <Route path="/Home" element={<Home />}></Route>
                        <Route
                            path="/editor/:roomId"
                            element={<EditorPageContainer />}
                        ></Route>
                    </Routes >
                </RecoilRoot >
            </BrowserRouter >
        </>
    );
}

export default App;