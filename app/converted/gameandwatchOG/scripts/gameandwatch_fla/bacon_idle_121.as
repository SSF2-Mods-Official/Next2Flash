package gameandwatch_fla
{
    import flash.display.MovieClip;
    import flash.events.Event;

    public dynamic class bacon_idle_121 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var food:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var time:*;
        public var MAX_TIME:*;
        public var rotationSpeed:*;
        public var foodstuff:*;
        public var transparent:*;

        public function bacon_idle_121()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 11, this.frame12, 12, this.frame13, 13, this.frame14, 14, this.frame15);
        }

        public function done(_arg_1:Event=null):*
        {
            this.self.destroyTimer(this.timerDone);
            this.self.destroyTimer(this.rotate);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.done);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.done);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.done);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.done);
            this.self.stancePlayFrame("done");
        }

        public function timerDone(_arg_1:Event=null):*
        {
            this.time++;
            if (this.time >= this.MAX_TIME)
            {
                this.done();
            };
        }

        public function rotate():*
        {
            var _local_1:* = this.self.getRotation();
            this.self.setRotation((_local_1 + this.rotationSpeed));
        }

        public function flicker():*
        {
            this.self.getStanceMC().alpha = ((this.transparent) ? 0 : 1);
            this.transparent = (!(this.transparent));
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.time = 0;
            this.MAX_TIME = 50;
            this.rotationSpeed = SSF2API.randomInteger(25, 70);
            if (this.self && SSF2API.isReady())
            {
                SSF2API.print("AHH MOTHERLAND");
                this.foodstuff = (SSF2API.randomInteger(1, 3) * 2);
                this.food.gotoAndStop(this.foodstuff);
                this.self.updateAttackBoxStats(1, {"priority":this.foodstuff});
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.done);
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.done);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.done);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.done);
                this.self.createTimer(1, -1, this.timerDone);
                this.self.createTimer(1, -1, this.rotate);
            };
        }

        internal function frame4():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame5():*
        {
            this.transparent = true;
            this.self.createTimer(1, -1, this.flicker);
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.updateProjectileStats({"gravity":0});
        }

        internal function frame12():*
        {
            this.self.destroy();
        }

        internal function frame13():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.rotationSpeed = 0;
            if (this.food != null)
            {
                this.food.gotoAndStop(this.self.getAttackBoxStat(1, "priority"));
            };
        }

        internal function frame14():*
        {
            this.self.stancePlayFrame("suspend");
        }

        internal function frame15():*
        {
            this.self = SSF2API.getProjectile(this);
            this.time = 0;
            this.MAX_TIME = 50;
            this.rotationSpeed = SSF2API.randomInteger(25, 70);
            if (this.self && SSF2API.isReady())
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.done);
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.done);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.done);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.done);
                this.self.createTimer(1, -1, this.timerDone);
                this.self.createTimer(1, -1, this.rotate);
                this.self.stancePlayFrame("loop");
            };
        }


    }
}

