// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//bm_misstext

package 
{
    import flash.display.MovieClip;

    public dynamic class bm_misstext extends MovieClip 
    {

        public function bm_misstext()
        {
            addFrameScript(21, this.frame22);
        }

        internal function frame22():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}//package 

