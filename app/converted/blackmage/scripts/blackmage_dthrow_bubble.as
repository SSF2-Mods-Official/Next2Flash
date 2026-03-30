package
{
    import flash.display.MovieClip;

    public dynamic class blackmage_dthrow_bubble extends MovieClip
    {

        public function blackmage_dthrow_bubble()
        {
            super();
            addFrameScript(12, this.frame13);
        }

        internal function frame13():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

