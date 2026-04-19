// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//trail_bmage_utilt

package 
{
    import flash.display.MovieClip;

    public dynamic class trail_bmage_utilt extends MovieClip 
    {

        public function trail_bmage_utilt()
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

