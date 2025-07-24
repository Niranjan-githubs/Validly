import { doc, setDoc, getDoc } from 'firebase/firestore';
import { db } from '../firebase';
import { User } from 'firebase/auth';

export const storeUserOutput = async (user: User, output: any) => {
  try {
    await setDoc(doc(db, 'outputs', user.uid), {
      output,
      updatedAt: new Date()
    });
  } catch (error) {
    console.error('Error storing user output:', error);
    throw error;
  }
};

export const getUserOutput = async (user: User) => {
  try {
    const docRef = doc(db, 'outputs', user.uid);
    const docSnap = await getDoc(docRef);

    if (docSnap.exists()) {
      return docSnap.data();
    }
    return null;
  } catch (error) {
    console.error('Error getting user output:', error);
    throw error;
  }
}; 