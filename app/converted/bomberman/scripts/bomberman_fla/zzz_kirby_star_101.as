package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class zzz_kirby_star_101 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var projectile:*;

        public function zzz_kirby_star_101()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (SSF2API.isReady() && parent && this.self)
            {
                this.projectile = this.self.getGlobalVariable("bombCharge");
                if (this.projectile != null)
                {
                    this.projectile.destroy();
                };
                this.self.setGlobalVariable("bombCharge", null);
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
            };
        }


    }
}

