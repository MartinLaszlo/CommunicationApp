import StartPage from "./StartPage";
import DirectMessage from "./DirectMessage"
import AuthPage from "./AuthPage";
import Settings from "./Settings"

const getPageContent = (page) => {
    switch (page) {
        case 'authpage':
            return <AuthPage />;
        case 'start':
            return <StartPage />
        case 'peers':
            return <h1 className="text-center">mail</h1>;
        case 'direct':
            return <DirectMessage />;
        case 'settings':
            return <Settings/>;
        default:
            return <AuthPage />;
    }
};
export default getPageContent;
