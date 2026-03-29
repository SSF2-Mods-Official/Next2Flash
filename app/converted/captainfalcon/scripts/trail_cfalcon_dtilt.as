package
{
    import flash.display.MovieClip;

    public dynamic class trail_cfalcon_dtilt extends MovieClip
    {

        public function trail_cfalcon_dtilt()
        {
            super();
            addFrameScript(5, this.frame6);
        }

        internal function frame6():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

