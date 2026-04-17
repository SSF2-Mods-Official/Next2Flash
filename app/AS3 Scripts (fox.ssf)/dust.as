// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//dust

package 
{
    import flash.display.MovieClip;

    public dynamic class dust extends MovieClip 
    {

        public function dust()
        {
            addFrameScript(10, this.frame11);
        }

        internal function frame11():*
        {
            if (((!(root == null)) && (!(parent == null))))
            {
                parent.removeChild(this);
            };
        }


    }
}//package 

