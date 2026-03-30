package
{
    import flash.display.MovieClip;

    public dynamic class AxeWind extends MovieClip
    {

        public function AxeWind()
        {
            super();
            addFrameScript(8, this.frame9);
        }

        internal function frame9():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

