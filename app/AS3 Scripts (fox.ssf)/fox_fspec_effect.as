// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fspec_effect

package 
{
    import flash.display.MovieClip;

    public dynamic class fox_fspec_effect extends MovieClip 
    {

        public function fox_fspec_effect()
        {
            addFrameScript(8, this.frame9);
        }

        internal function frame9():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}//package 

