// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//trail_bmage_pummel

package 
{
    import flash.display.MovieClip;

    public dynamic class trail_bmage_pummel extends MovieClip 
    {

        public function trail_bmage_pummel()
        {
            addFrameScript(6, this.frame7);
        }

        internal function frame7():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}//package 

