package
{
    import flash.display.MovieClip;

    public dynamic class kirby_afterimage extends MovieClip
    {

        public var self:*;

        public function kirby_afterimage()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
        }

        internal function frame9():*
        {
            this.self.destroy();
        }


    }
}

