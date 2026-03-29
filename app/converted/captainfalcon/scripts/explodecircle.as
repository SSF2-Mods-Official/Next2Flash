package
{
    import flash.display.MovieClip;

    public dynamic class explodecircle extends MovieClip
    {

        public function explodecircle()
        {
            super();
            addFrameScript(16, this.frame17);
        }

        internal function frame17():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

