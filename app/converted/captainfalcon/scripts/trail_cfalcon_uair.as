package
{
    import flash.display.MovieClip;

    public dynamic class trail_cfalcon_uair extends MovieClip
    {

        public function trail_cfalcon_uair()
        {
            super();
            addFrameScript(7, this.frame8);
        }

        internal function frame8():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

