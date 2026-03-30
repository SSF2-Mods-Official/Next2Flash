package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_lose_16 extends MovieClip
    {

        public function bomberman_lose_16()
        {
            super();
            addFrameScript(12, this.frame13);
        }

        internal function frame13():*
        {
            this.gotoAndPlay("loop");
        }


    }
}

