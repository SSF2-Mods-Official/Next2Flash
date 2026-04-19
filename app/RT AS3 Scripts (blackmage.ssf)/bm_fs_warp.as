// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//bm_fs_warp

package 
{
    import flash.display.MovieClip;

    public dynamic class bm_fs_warp extends MovieClip 
    {

        public function bm_fs_warp()
        {
            addFrameScript(10, this.frame11);
        }

        internal function frame11():*
        {
            stop();
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}//package 

