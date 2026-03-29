package
{
    import flash.display.MovieClip;

    public dynamic class trail_cfalcon_nair extends MovieClip
    {

        public function trail_cfalcon_nair()
        {
            super();
            addFrameScript(11, this.frame12);
        }

        internal function frame12():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

