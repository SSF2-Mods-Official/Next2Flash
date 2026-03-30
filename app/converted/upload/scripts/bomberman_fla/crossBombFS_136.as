package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class crossBombFS_136 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var character:*;

        public function crossBombFS_136()
        {
            super();
            addFrameScript(0, this.frame1, 20, this.frame21, 21, this.frame22, 30, this.frame31, 41, this.frame42, 42, this.frame43);
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
                this.self.addToCamera();
            };
        }

        internal function frame21():*
        {
            this.self.stancePlayFrame("start");
        }

        internal function frame22():*
        {
            this.self.updateProjectileStats({"gravity":0});
            SSF2API.getCamera().shake(10);
        }

        internal function frame31():*
        {
            this.self.playSound("bombexplode");
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
        }

        internal function frame42():*
        {
            this.self.removeFromCamera();
        }

        internal function frame43():*
        {
            this.self.destroy();
        }


    }
}

