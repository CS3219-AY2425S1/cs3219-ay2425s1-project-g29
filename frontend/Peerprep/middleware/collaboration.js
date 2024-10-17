export default function ({ store, redirect, route }) {
    const collaborationInfo = store.state.collaboration.collaborationInfo;
    if (collaborationInfo) {
      // If collaborationInfo exists, ensure the user can access the collaboration page
      // Optionally, redirect to the collaboration page if they're not on it
      if (route.name !== 'collaboration-page') {
        return redirect('/collaboration-page');
      }
    } else {
      // If collaborationInfo doesn't exist and the user is trying to access the collaboration page, redirect them
      if (route.name === 'collaboration-page') {
        return redirect('/');
      }
    }
  }
  