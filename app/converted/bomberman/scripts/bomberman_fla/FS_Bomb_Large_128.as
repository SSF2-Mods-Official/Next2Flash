package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class FS_Bomb_Large_128 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var character:*;

        public function FS_Bomb_Large_128()
        {
            super();
            addFrameScript(0, this.frame1, 20, this.frame21, 21, this.frame22, 25, this.frame26);
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

        internal function frame21():*
        {
            this.self.stancePlayFrame("start");
        }

        internal function frame22():*
        {
            this.self.attachEffect("effect_explosion", {
                "scaleX":1.81,
                "scaleY":1.81
            });
            SSF2API.getCamera().shake(10);
            SSF2API.playSound("bomberman_explode");
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
        }

        internal function frame26():*
        {
            this.self.destroy();
        }


    }
}

