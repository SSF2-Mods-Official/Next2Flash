package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class CollisonBox_8 extends MovieClip
    {

        public function CollisonBox_8()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.visible = false;
        }


    }
}

