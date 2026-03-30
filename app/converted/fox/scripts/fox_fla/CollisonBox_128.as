package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class CollisonBox_128 extends MovieClip
    {

        public function CollisonBox_128()
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

