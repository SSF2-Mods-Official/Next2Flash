package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Firemen_124 extends MovieClip
    {

        public var self:*;

        public function Firemen_124()
        {
            super();
            addFrameScript(0, this.frame1, 9, this.frame10);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
        }

        internal function frame10():*
        {
            this.self.destroy();
        }


    }
}

