// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//trail_bmage_ftilt

package 
{
    import flash.display.MovieClip;

    public dynamic class trail_bmage_ftilt extends MovieClip 
    {

        public function trail_bmage_ftilt()
        {
            addFrameScript(7, this.frame8);
        }

        internal function frame8():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}//package 

