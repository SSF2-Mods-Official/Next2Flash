package
{
    public class KirbyFinalSmashController
    {

        internal const CAPTURE_TIME:int = 2;
        internal const COOK_TIME:int = 70;
        internal const ITEM_SPAWN_RATE:int = 5;
        internal const ITEM_SPAWN_CAP:int = 30;
        internal var state:int;
        internal var self:*;
        internal var queue:Array;
        internal var foes:Array;
        internal var items:Array;
        internal var captureTimer:FrameTimer;
        internal var cookTimer:FrameTimer;
        internal var spawnTimer:FrameTimer;
        internal var itemsToSpawn:int;

        public function KirbyFinalSmashController(_arg_1:*):void
        {
            this.self = _arg_1;
            this.queue = new Array();
            this.foes = new Array();
            this.state = 0;
            this.captureTimer = new FrameTimer(this.CAPTURE_TIME);
            this.cookTimer = new FrameTimer(this.COOK_TIME);
            this.spawnTimer = new FrameTimer(this.ITEM_SPAWN_RATE);
            this.itemsToSpawn = 0;
            this.items = new Array();
            this.items.push("beamsword");
            this.items.push("bobomb");
            this.items.push("mrsaturn");
            this.items.push("capsule");
            this.items.push("capsule_ex");
            this.items.push("fooditem");
            this.items.push("maximumtomato");
            this.items.push("heartContainer");
            this.items.push("energytank");
            this.items.push("bumper");
            this.items.push("explodingtag");
            this.items.push("fan");
            this.items.push("greenshell");
        }

        private function findFoes():void
        {
            var _local_1:int;
            var _local_2:Array = SSF2API.getCharacters();
            for (_local_1 = 0; _local_1 < _local_2.length; _local_1++)
            {
                if (_local_2[_local_1] && !(_local_2[_local_1].isDisposed()) && (_local_2[_local_1].getID() !== this.self.getID()))
                {
                    this.queue.push(_local_2[_local_1]);
                };
            };
            _local_2 = SSF2API.getItems();
            for (_local_1 = 0; _local_1 < _local_2.length; _local_1++)
            {
                if (_local_2[_local_1] && !(_local_2[_local_1].isDisposed()) && (_local_2[_local_1].getID() !== this.self.getID()))
                {
                    this.queue.push(_local_2[_local_1]);
                };
            };
            this.state = 1;
        }

        private function snagNextFoe():void
        {
            var _local_1:* = undefined;
            this.captureTimer.tick();
            if (this.captureTimer.completed)
            {
                this.captureTimer.reset();
                if (this.queue.length <= 0)
                {
                    this.state = 2;
                }
                else
                {
                    _local_1 = this.queue[0];
                    this.queue.splice(0, 1);
                    if (_local_1 && !(_local_1.isDisposed()))
                    {
                        this.foes.push(new KirbyFinalSmashFoe(this.self, _local_1));
                    };
                };
            };
        }

        private function processFoes():void
        {
            for (var _local_1:int = 0; _local_1 < this.foes.length; _local_1++)
            {
                this.foes[_local_1].update();
            };
        }

        private function allFoesCooking():Boolean
        {
            for (var _local_1:int = 0; _local_1 < this.foes.length; _local_1++)
            {
                if (!(this.foes[_local_1].isCooking()) && !(this.foes[_local_1].isBroken()))
                {
                    return false;
                };
            };
            return true;
        }

        private function allFoesReleased():Boolean
        {
            for (var _local_1:int = 0; _local_1 < this.foes.length; _local_1++)
            {
                if (!this.foes[_local_1].isReleased())
                {
                    return false;
                };
            };
            return true;
        }

        public function release():void
        {
            this.state = 5;
            for (var _local_1:int = 0; _local_1 < this.foes.length; _local_1++)
            {
                if (!this.foes[_local_1].isBroken())
                {
                    this.itemsToSpawn++;
                };
            };
            if (this.itemsToSpawn > this.ITEM_SPAWN_CAP)
            {
                this.itemsToSpawn = this.ITEM_SPAWN_CAP;
            };
        }

        public function spawnRandomItem():void
        {
            var _local_1:* = null;
            var _local_2:Number = NaN;
            var _local_3:* = undefined;
            _local_2 = ((SSF2API.random() * 4) - 2);
            _local_1 = this.items[Math.round((SSF2API.random() * (this.items.length - 1)))];
            _local_3 = this.self.generateItem(_local_1, false, false);
            if (_local_3 != null)
            {
                _local_3.safeMove(((this.self.isFacingRight()) ? 40 : -40), 0);
                _local_3.setXSpeed(_local_2);
                if (_local_1 != "heartContainer")
                {
                    _local_3.setYSpeed(-12);
                };
            };
        }

        private function checkItemSpawn():void
        {
            if (this.itemsToSpawn <= 0)
            {
                this.self.stancePlayFrame("outro");
                this.state = 6;
            }
            else
            {
                this.spawnTimer.tick();
                if (this.spawnTimer.completed)
                {
                    this.spawnTimer.reset();
                    this.spawnRandomItem();
                    this.itemsToSpawn--;
                };
            };
        }

        public function update():void
        {
            if (this.state === 0)
            {
                this.findFoes();
            }
            else if (this.state === 1)
            {
                this.snagNextFoe();
            }
            else if (this.state === 2)
            {
                if (this.allFoesCooking())
                {
                    this.state = 3;
                    this.self.stancePlayFrame("start");
                };
            }
            else if (this.state === 3)
            {
                this.cookTimer.tick();
                if (this.cookTimer.completed)
                {
                    this.self.stancePlayFrame("end");
                    this.state = 4;
                };
            }
            else if (this.state === 4)
            {
            }
            else if (this.state === 5)
            {
                this.checkItemSpawn();
            }
            else if (this.state === 6)
            {
            };
            this.processFoes();
        }


    }
}

