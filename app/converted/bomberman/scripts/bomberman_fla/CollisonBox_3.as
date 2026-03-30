package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class CollisonBox_3 extends MovieClip
    {

        public function CollisonBox_3()
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

