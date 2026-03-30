package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_stunned_88 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var projectile:*;

        public function bomberman_stunned_88()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (parent && SSF2API.isReady() && this.self)
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

