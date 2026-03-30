package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class fsbombsmall_121 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var character:*;

        public function fsbombsmall_121()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9, 9, this.frame10, 13, this.frame14);
        }

        public function hitExplode(_arg_1:*=null):*
        {
            if (_arg_1.data.opponent.getType() == "SSF2Character")
            {
                this.explode();
            };
        }

        public function explode(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.PROJ_COLLIDE, this.hitExplode);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.explode);
            this.self.stancePlayFrame("explode");
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.self.addEventListener(SSF2Event.PROJ_COLLIDE, this.hitExplode);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.explode);
            };
        }

        internal function frame9():*
        {
            this.self.stancePlayFrame("level1");
        }

        internal function frame10():*
        {
            this.self.attachEffect("effect_explosion");
            SSF2API.getCamera().shake(3);
            SSF2API.playSound("bomberman_explode");
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
        }

        internal function frame14():*
        {
            this.self.destroy();
        }


    }
}

